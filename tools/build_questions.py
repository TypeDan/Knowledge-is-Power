"""Compile original question text into the Lua bank shipped with the mod."""
from pathlib import Path
import json

root = Path(__file__).resolve().parents[1]
rows = []
seen = set()
for line in (root/'questions/questions.tsv').read_text(encoding='utf-8').splitlines():
    category, question, *answers = line.split('|')
    assert category in ('general', 'christmas')
    assert len(answers) == 4 and len(set(answers)) == 4, question
    assert question not in seen, question
    assert len(question) < 160 and max(map(len, answers)) < 85, question
    seen.add(question)
    quote = lambda value: json.dumps(value, ensure_ascii=False)
    rows.append('    {category='+quote(category)+',text='+quote(question)+',options={'+','.join(map(quote,answers))+'},correct=1},')
text = '-- Generated from questions/questions.tsv; answer positions shuffle each round.\nKIP_QUESTIONS = {\n'+'\n'.join(rows)+'\n}\n'
(root/'assets/scar/trivia/questions.scar').write_text(text, encoding='utf-8')
print(f'Compiled {len(rows)} unique questions.')
