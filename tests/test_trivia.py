"""Exercise the actual Lua trivia state machine, authority and resource effects."""
from pathlib import Path
from lupa import LuaRuntime
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[1]
lua = LuaRuntime()
lua.execute('Core_RegisterModule=function() end; import=function() end')
for name in ('questions.scar','knowledge_ui.scar','knowledge.scar'):
    lua.execute((root/'assets/scar/trivia'/name).read_text(encoding='utf-8'))
lua.execute('''
RT_Food=1;RT_Wood=2;RT_Gold=3;RT_Stone=4;AGS_BP_VILLAGER="villager"
players={{id=41,slot=3,team=1,age=2,human=true},{id=12,slot=1,team=1,age=1,human=true},
 {id=73,slot=8,team=2,age=4,human=true},{id=18,slot=5,team=2,age=3,human=false}}
function find(id) for _,p in ipairs(players) do if p.id==id then return p end end end
World_GetPlayerCount=function() return #players end
Core_GetPlayersTableEntryFromIndex=function(i) return players[i] end
Player_GetSlotIndex=function(id) return find(id).slot end
Player_GetTeam=function(id) return find(id).team end
Player_GetCurrentAge=function(id) return find(id).age end
Player_IsHuman=function(id) return find(id).human end
Player_GetDisplayName=function(id) return {LocString="Name "..id} end
Game_GetLocalPlayer=function() return localPlayer end
UI_IsReplay=function() return false end
UI_CreateEventCue=function() end;Loc_Empty=function() return "" end
UI_SetDataContext=function(name,data) context=data end
UI_CreateCommand=function(name) return name end
UI_CreateDataContext=function(data) return data end
UI_AddChild=function(a,b,c,args) xaml=args.Xaml end
Rule_AddInterval=function() end;Rule_Remove=function() end;Rule_Exists=function() return false end
registered={};Network_RegisterEvent=function(name) registered[name]=true end
Network_CallEvent=function(name,message) lastNetwork={name,message} end
EGroup_ForEach=function(group,fn) for i,e in ipairs(group) do fn(group,i,e) end end
Entity_IsAlive=function(e) return not e.dead end
Entity_IsOfType=function(e,t) return e.kind==t end
Entity_GetID=function(e) return e.id end
Entity_Kill=function(e) assert(not e.dead);e.dead=true end
Player_GetAllEntities=function(id) return entities[id] or {} end
Player_GetResource=function(id,resource) return resources[id][resource] end
Player_AddResource=function(id,resource,amount)
    resources[id][resource]=resources[id][resource]+amount
    assert(resources[id][resource]>=0)
end
local seed=1; randomCalls=0
World_GetRand=function(a,b)
    randomCalls=randomCalls+1;seed=(seed*16807)%2147483647
    return a+seed%(b-a+1)
end
function reset()
    KIP={running=true,time=0,round=0,nextRound=180,teams={},turns={},passesUsed={},deck={},deckIndex=1}
    KIP_UI={created=false,open=false,assignment="",submitted=""}
    KIP_CONFIG.general=true;KIP_CONFIG.christmas=true
    resources={};entities={};localPlayer=12
    for _,p in ipairs(players) do
        p.isEliminated=false;resources[p.id]={1000,1000,1000,1000};entities[p.id]={}
    end
end
reset()
assert(KIP_CONFIG.interval==180 and KIP_CONFIG.answerSeconds==20)
for i=1,179 do KIP_Tick() end
assert(KIP.round==0)
KIP_Tick();assert(KIP.round==1 and KIP.nextRound==360 and #KIP.teams==2)
local team=KIP.teams[1]
assert(team.members[1]==12 and team.members[2]==41 and team.deadline==200)
assert(KIP.teams[1].question.id~=KIP.teams[2].question.id)
assert(KIP.teams[2].answerer==73) -- AI teammates never take a human's turn.
assert(team.costs[1]+team.costs[3]==math.floor(team.prize/2))
assert(math.abs(team.costs[1]-team.costs[3])<=1)
local expected=team.prize
local correct=team.question.correct
local other=team.answerer==12 and 41 or 12
assert(not KIP_AnswerNetwork(other,'1:'..correct))
assert(not KIP_AnswerNetwork(73,'0:'..correct))
assert(not KIP_AnswerNetwork(999,'1:'..correct))
for _,bad in ipairs({'1:0','1:5','1:1:1','1:1x','-1:1','1:2.0',string.rep('1',40)}) do
    assert(not KIP_AnswerNetwork(team.answerer,bad))
end
assert(KIP_AnswerNetwork(team.answerer,'1:'..correct))
assert(not KIP_AnswerNetwork(team.answerer,'1:'..correct))
for resource=1,4 do
    assert(resources[12][resource]+resources[41][resource]==2000+expected)
    assert(math.abs(resources[12][resource]-resources[41][resource])<=1)
end
assert(resources[73][1]==1000 and resources[18][1]==1000)

-- Wrong: the frozen share of the team bill or 15% villagers, no partial bill.
reset();KIP_StartRound(KIP_LivePlayers());team=KIP.teams[1]
local insufficient=team.costs[3]-1
resources[41]={1000,insufficient,1000,1000}
for i=1,35 do table.insert(entities[41],{id=100-i,kind='villager'}) end
table.insert(entities[41],{id=0,kind='trader'})
table.insert(entities[41],{id=1,kind='villager',dead=true})
local wrong=team.question.correct%4+1
assert(KIP_AnswerNetwork(team.answerer,'1:'..wrong))
for r=1,4 do assert(resources[12][r]==1000-team.costs[1]) end
assert(resources[41][1]==1000 and resources[41][2]==insufficient)
assert(#KIP_PlayerVillagers(41)==29 and team.effects[3].lost==6)
assert(not entities[41][36].dead) -- Trader is never a villager casualty.
for _,count in ipairs({0,1,6,10,11,20,35,40,101}) do
    entities[41]={}
    for i=1,count do table.insert(entities[41],{id=i,kind='villager'}) end
    local effect=KIP_ApplyPenalty(41,150)
    assert(effect.lost==math.ceil(count*15/100) and #KIP_PlayerVillagers(41)==count-math.ceil(count*15/100))
end

-- Every age has a team bill exactly half (rounded down) of the prize.
for age,amount in ipairs({450,675,900,1350}) do
    reset();players[1].age=age;players[2].age=age;KIP_StartRound(KIP_LivePlayers())
    assert(KIP.teams[1].prize==amount)
    assert(KIP.teams[1].costs[1]+KIP.teams[1].costs[3]==math.floor(amount/2))
end
players[1].age=2;players[2].age=1
reset();KIP_StartRound(KIP_LivePlayers());team=KIP.teams[1]
local original=team.prize;find(team.answerer).age=4
assert(team.prize==original) -- Displayed stake is fixed when the question opens.
players[1].age=2;players[2].age=1

-- Deadline is 20 game seconds. Delayed packets cannot answer after expiry.
reset();KIP_StartRound(KIP_LivePlayers());team=KIP.teams[1]
for i=1,19 do KIP_Tick() end
assert(team.status=='pending')
KIP_Tick();assert(team.status=='timeout' and resources[12][1]==1000-team.costs[1])
assert(not KIP_AnswerNetwork(team.answerer,'1:'..team.question.correct))
for i=1,159 do KIP_Tick() end
assert(KIP.round==1)
KIP_Tick();assert(KIP.round==2)

-- Teammates rotate before repeating; leave/reassignment never rewards a dead player.
reset();local previous
for i=1,8 do
    KIP_StartRound(KIP_LivePlayers())
    if i%2==0 then assert(previous~=KIP.teams[1].answerer) end
    previous=KIP.teams[1].answerer
end
reset();KIP_StartRound(KIP_LivePlayers());team=KIP.teams[1]
local departed=team.answerer;find(departed).isEliminated=true
KIP_Tick();assert(team.answerer~=departed and team.deadline==20)
assert(not KIP_AnswerNetwork(departed,'1:'..team.question.correct))
assert(KIP_AnswerNetwork(team.answerer,'1:'..team.question.correct))
assert(resources[departed][1]==1000)
assert(resources[team.answerer][1]==1000+team.prize)

-- AI-only teams have exactly 50 successes per 100 simulated coin flips.
reset();players[3].human=false
local actualRng=World_GetRand;local successes=0
for coin=1,100 do
    World_GetRand=function(a,b) if a==1 and b==100 then return coin end return actualRng(a,b) end
    KIP_StartRound(KIP_LivePlayers());local ai=KIP.teams[2]
    assert(not ai.human and ai.aiAt>=5 and ai.aiAt<=18)
    if ai.aiCorrect then successes=successes+1 end
end
assert(successes==50);World_GetRand=actualRng;players[3].human=true

-- Unequal team sizes have equal total prizes and bills at every age.
local originalPlayers=players
for _,size in ipairs({2,3,4}) do
    for age,prize in ipairs({450,675,900,1350}) do
        players={}
        for i=1,size+2 do
            table.insert(players,{id=i*11,slot=i,team=i<=size and 1 or 2,age=age,human=true})
        end
        reset()
        for _,p in ipairs(players) do resources[p.id]={10000,10000,10000,10000} end
        local totalPaid={}
        for round=1,size do
            KIP_StartRound(KIP_LivePlayers())
            for _,entry in ipairs(KIP.teams) do
                local bill=0
                for _,id in ipairs(entry.members) do
                    local cost=entry.costs[Player_GetSlotIndex(id)]
                    bill=bill+cost;totalPaid[id]=(totalPaid[id] or 0)+cost
                end
                assert(bill==math.floor(prize/2) and entry.prize==prize)
                assert(KIP_AnswerNetwork(entry.answerer,tostring(round)..':'..(entry.question.correct%4+1)))
            end
        end
        for i=1,size do assert(totalPaid[players[i].id]==math.floor(prize/2)) end -- Remainders rotate fairly.
        KIP_StartRound(KIP_LivePlayers())
        for _,entry in ipairs(KIP.teams) do
            local before=0
            for _,id in ipairs(entry.members) do before=before+resources[id][1] end
            assert(KIP_AnswerNetwork(entry.answerer,tostring(entry.round)..':'..entry.question.correct))
            local after=0
            for _,id in ipairs(entry.members) do after=after+resources[id][1] end
            assert(after-before==prize)
        end
    end
end
players=originalPlayers;reset()

-- A team pass has no resource/villager/RNG effect, and only the chosen human can use it.
KIP_StartRound(KIP_LivePlayers());team=KIP.teams[1]
local passer=team.answerer
local helper=passer==12 and 41 or 12
for _,id in ipairs(team.members) do
    resources[id]={0,0,0,0}
    for i=1,11 do table.insert(entities[id],{id=i,kind='villager'}) end
end
assert(not KIP_PassNetwork(helper,'1'))
assert(not KIP_PassNetwork(999,'1'))
assert(not KIP_PassNetwork(18,'1'))
for _,bad in ipairs({'0','2','1:1','1x','-1','1.0',string.rep('1',40)}) do assert(not KIP_PassNetwork(passer,bad)) end
assert(not KIP_PassNetwork(passer,{}))
find(passer).isEliminated=true;assert(not KIP_PassNetwork(passer,'1'));find(passer).isEliminated=false
KIP.time=team.deadline;assert(not KIP_PassNetwork(passer,'1'));KIP.time=0
local before=randomCalls
assert(KIP_PassNetwork(passer,'1'))
assert(team.status=='passed' and not KIP_HasPass(team) and randomCalls==before)
assert(KIP_HasPass(KIP.teams[2]) and KIP.teams[2].status=='pending')
for _,id in ipairs(team.members) do
    assert(#KIP_PlayerVillagers(id)==11)
    for r=1,4 do assert(resources[id][r]==0) end
end
assert(not KIP_PassNetwork(passer,'1'))
assert(not KIP_AnswerNetwork(passer,'1:'..team.question.correct))
assert(not KIP_SuggestNetwork(helper,'1:1'))
for i=1,20 do KIP_Tick() end
assert(team.status=='passed' and #KIP_PlayerVillagers(passer)==11)
Knowledge_OnGameRestore();assert(not KIP_HasPass(team) and registered.KIP_PassNetwork)
for i=2,5 do
    KIP_StartRound(KIP_LivePlayers());team=KIP.teams[1]
    assert(not KIP_HasPass(team))
    assert(not KIP_PassNetwork(team.answerer,tostring(i)))
end
assert(KIP_HasPass(KIP.teams[2])) -- Other teams retain their own pass.
assert(KIP_PassNetwork(KIP.teams[2].answerer,'5'))

-- Answer/pass races settle exactly once; old saves have an unused pass.
reset();KIP.passesUsed=nil;KIP_StartRound(KIP_LivePlayers());team=KIP.teams[1]
assert(KIP_HasPass(team))
assert(KIP_AnswerNetwork(team.answerer,'1:'..team.question.correct))
assert(not KIP_PassNetwork(team.answerer,'1') and KIP_HasPass(team))
KIP_StartRound(KIP_LivePlayers());team=KIP.teams[1]
find(team.answerer).isEliminated=true;KIP_Tick()
assert(KIP_PassNetwork(team.answerer,'2')) -- Reassigned answerer can spend the same team pass.

-- AI pass decisions use affordability, never their hidden correct/incorrect coin flip.
for _,wouldBeCorrect in ipairs({true,false}) do
    reset();players[3].human=false;KIP_StartRound(KIP_LivePlayers())
    local ai=KIP.teams[2];ai.aiCorrect=wouldBeCorrect
    resources[73]={0,0,0,0};entities[73]={{id=1,kind='villager'}}
    KIP.time=ai.aiAt-1;KIP_Tick()
    assert(ai.status=='passed' and #KIP_PlayerVillagers(73)==1)
    KIP_StartRound(KIP_LivePlayers());ai=KIP.teams[2];ai.aiCorrect=false
    KIP.time=ai.aiAt-1;KIP_Tick()
    assert(ai.status=='wrong' and #KIP_PlayerVillagers(73)==0)
    players[3].human=true
end

-- No repeated questions before the enabled bank is exhausted; options remain a permutation.
reset();local seen={};local answerPositions={}
for i=1,#KIP_QUESTIONS do
    local q=KIP_NextQuestion();assert(not seen[q.id]);seen[q.id]=true
    answerPositions[q.correct]=true
    assert(q.options[q.correct]==KIP_QUESTIONS[q.id].options[1])
end
for i=1,4 do assert(answerPositions[i]) end
local last=KIP.lastQuestion;assert(KIP_NextQuestion().id~=last)
for _,category in ipairs({'general','christmas'}) do
    reset();KIP_CONFIG.general=category=='general';KIP_CONFIG.christmas=category=='christmas'
    for i=1,500 do assert(KIP_NextQuestion().category==category) end
end
reset();Knowledge_SetupSettings({section_knowledge_trivia={general_questions=false,christmas_questions=false}})
assert(KIP_NextQuestion()==nil);Knowledge_OnPlay();assert(not KIP.running)

-- Team questions remain distinct across deck reshuffles.
reset()
for i=1,500 do
 KIP_StartRound(KIP_LivePlayers())
 assert(KIP.teams[1].question.id~=KIP.teams[2].question.id)
end

-- Suggestions are per sender, scoped to their team, and cannot settle a round.
reset();KIP_StartRound(KIP_LivePlayers());team=KIP.teams[1]
helper=team.answerer==12 and 41 or 12
local before=randomCalls
assert(KIP_SuggestNetwork(helper,'1:2'))
assert(team.suggestions[Player_GetSlotIndex(helper)]==2 and team.status=='pending')
assert(resources[12][1]==1000 and resources[41][1]==1000 and randomCalls==before)
assert(KIP.teams[2].suggestions[Player_GetSlotIndex(helper)]==nil)
assert(not KIP_SuggestNetwork(helper,'1:2'))
assert(KIP_SuggestNetwork(helper,'1:4')) -- Advice may change until the final answer.
assert(team.suggestions[Player_GetSlotIndex(helper)]==4)
assert(not KIP_SuggestNetwork(team.answerer,'1:1'))
assert(not KIP_SuggestNetwork(18,'1:1')) -- An AI cannot impersonate a human helper.
assert(not KIP_SuggestNetwork(999,'1:1'))
for _,bad in ipairs({'0:1','2:1','1:0','1:5','1:1:1','1:1x','-1:1','1:2.0',string.rep('1',40)}) do
    assert(not KIP_SuggestNetwork(helper,bad))
end
assert(not KIP_SuggestNetwork(helper,{}))
find(helper).isEliminated=true;assert(not KIP_SuggestNetwork(helper,'1:3'))
find(helper).isEliminated=false
local oldTeam=find(helper).team;find(helper).team=99
assert(not KIP_SuggestNetwork(helper,'1:3'));find(helper).team=oldTeam
KIP.time=team.deadline;assert(not KIP_SuggestNetwork(helper,'1:3'));KIP.time=0
assert(KIP_AnswerNetwork(team.answerer,'1:'..team.question.correct))
assert(not KIP_SuggestNetwork(helper,'1:3'))
KIP_StartRound(KIP_LivePlayers());assert(next(KIP.teams[1].suggestions)==nil)
assert(not KIP_SuggestNetwork(helper,'1:3'))

-- If a helper takes over, their old advice is not a final answer.
reset();KIP_StartRound(KIP_LivePlayers());team=KIP.teams[1]
helper=team.answerer==12 and 41 or 12
assert(KIP_SuggestNetwork(helper,'1:2'))
find(team.answerer).isEliminated=true;KIP_Tick()
assert(team.answerer==helper and team.suggestions[Player_GetSlotIndex(helper)]==nil)
assert(team.status=='pending' and team.deadline==20)

-- UI: everyone on the team sees the question; only the answerer submits it.
reset();KIP_StartRound(KIP_LivePlayers());team=KIP.teams[1]
localPlayer=team.answerer;KIP_CreateUI()
assert(context.question==team.question.text and context.questionVisibility=='Visible' and context.enabled)
assert(context.visibility=='Visible' and context.payloads.A=='1:1')
before=randomCalls;KIP_RefreshUI();assert(randomCalls==before)
localPlayer=team.answerer==12 and 41 or 12;KIP_RefreshUI()
helper=localPlayer
assert(context.question==team.question.text and context.questionVisibility=='Visible' and context.enabled)
assert(context.answers.A and context.visibility=='Visible')
KIP_UIAnswer(context.payloads.B)
assert(lastNetwork[1]=='KIP_SuggestNetwork' and lastNetwork[2]=='1:2' and KIP_UI.submitted=='')
assert(KIP_SuggestNetwork(helper,lastNetwork[2]))
assert(context.backgrounds.B=='#FF426744' and context.backgrounds.A=='#FF182C39')
assert(string.find(context.suggestions,'Name '..helper..': B',1,true))
KIP_UIAnswer(context.payloads.D);assert(KIP_SuggestNetwork(helper,lastNetwork[2]))
assert(context.backgrounds.D=='#FF426744' and context.backgrounds.B=='#FF182C39')
localPlayer=team.answerer;KIP_RefreshUI()
assert(string.find(context.suggestions,'Name '..helper..': D',1,true))
assert(context.enabled and context.backgrounds.D=='#FF182C39')
localPlayer=73;KIP_RefreshUI()
assert(not string.find(context.suggestions,'Name '..helper,1,true)) -- Opposing team cannot see suggestions.
localPlayer=helper;find(helper).isEliminated=true;KIP_RefreshUI()
assert(not context.enabled);lastNetwork=nil;KIP_UIAnswer('1:1');assert(lastNetwork==nil)
find(helper).isEliminated=false
-- A restored older save with no suggestion table still renders.
team.suggestions=nil;KIP_RefreshUI();assert(context.suggestionsVisibility=='Visible')
localPlayer=team.answerer;KIP_RefreshUI();KIP_UIAnswer(context.payloads.A)
assert(lastNetwork[1]=='KIP_AnswerNetwork' and lastNetwork[2]=='1:1' and not context.enabled)
-- Pass control: helpers see availability, only answerer sends, and spent state persists.
reset();KIP_StartRound(KIP_LivePlayers());team=KIP.teams[1]
localPlayer=team.answerer;KIP_CreateUI()
assert(context.passLabel=='Pass (1)' and context.passEnabled and context.passPayload=='1')
localPlayer=team.answerer==12 and 41 or 12;KIP_RefreshUI()
lastNetwork=nil;KIP_UIPass('1');assert(lastNetwork==nil and not context.passEnabled)
localPlayer=team.answerer;KIP_RefreshUI();KIP_UIPass(context.passPayload)
assert(lastNetwork[1]=='KIP_PassNetwork' and lastNetwork[2]=='1' and not context.enabled and not context.passEnabled)
lastNetwork=nil;KIP_UIAnswer('1:1');KIP_UIPass('1');assert(lastNetwork==nil)
assert(KIP_PassNetwork(team.answerer,'1'))
assert(context.passLabel=='Pass used' and context.status=='Question passed.')
assert(context.result=='Team pass used. No reward or penalty.')
Knowledge_OnGameRestore();assert(context.passLabel=='Pass used' and not context.passEnabled)
KIP_StartRound(KIP_LivePlayers());team=KIP.teams[1];localPlayer=team.answerer;KIP_RefreshUI()
assert(context.passLabel=='Pass used' and context.enabled and not context.passEnabled)

-- Native player handles are opaque objects, not numbers or concatenable text.
reset();KIP_StartRound(KIP_LivePlayers());team=KIP.teams[1];localPlayer=team.answerer;KIP_CreateUI()
local handle={};local oldAnswerer=team.answerer
for i,id in ipairs(team.members) do if id==oldAnswerer then team.members[i]=handle end end
find(oldAnswerer).id=handle
team.answerer=handle;localPlayer=handle
local originalGetSlot=Player_GetSlotIndex
Player_GetSlotIndex=function(id) if id==handle then return 1 end return originalGetSlot(id) end
Player_GetDisplayName=function(id) return {LocString=id==handle and 'Opaque player' or ('Name '..id)} end
KIP_RefreshUI()
assert(KIP_UI.assignment=='1:1' and context.questionVisibility=='Visible')
-- UI receives a player wrapper separately from Core; slot keys bridge them.
team.costs[1]=100;KIP_RefreshUI()
assert(string.find(context.stakes,'you pay 100 of each',1,true))
team.status='correct';team.effects[1]={won=150};KIP_RefreshUI()
assert(string.find(context.result,'You received 150 of each resource.',1,true))
''')
ET.fromstring(lua.globals().xaml)
print('PASS: timing, answer/suggestion/pass authority, 3v2 and 4v2 shared bills, rotating remainders, match-long passes, restore, AI pass policy, 15% casualties, AI odds, no-repeat questions, rotation, teammate advice, UI privacy and XAML.')
