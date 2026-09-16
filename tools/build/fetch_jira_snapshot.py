#!/usr/bin/env python3
"""ดึง Epic/Story/Task (ไม่เอา Bug/Subtask) จาก Jira ทุกโปรเจกต์ → tools/build/jira-snapshot/<KEY>.json
ใช้ auth จาก ~/.config/jira-auth ผ่าน ~/.claude/scripts/jira.py (ห้าม print token)
รัน: python3 tools/build/fetch_jira_snapshot.py [KEY ...]
"""
import sys, json, pathlib, datetime, importlib.util
spec = importlib.util.spec_from_file_location('j', pathlib.Path.home() / '.claude/scripts/jira.py'); j = importlib.util.module_from_spec(spec); spec.loader.exec_module(j)
OUT = pathlib.Path(__file__).resolve().parent / 'jira-snapshot'
FIELDS = ['summary', 'issuetype', 'status', 'parent', 'duedate', 'customfield_10015', 'customfield_10022', 'customfield_10023', 'customfield_10020', 'assignee', 'labels', 'created', 'resolutiondate', 'priority']
KEYS = sys.argv[1:] or ['TAKRA', 'TAK', 'TI', 'TKH', 'ACL', 'TLS', 'TKRD']
for key in KEYS:
    issues, token = [], None
    while True:
        body = {'jql': f'project = {key} AND issuetype in (Epic, Story, Task, Feature) ORDER BY key ASC', 'maxResults': 100, 'fields': FIELDS}
        if token: body['nextPageToken'] = token
        s, r = j.call('POST', '/rest/api/3/search/jql', body)
        if s != 200: print(key, 'HTTP', s, str(r)[:200]); break
        for i in r.get('issues', []):
            f = i['fields']; sp = f.get('customfield_10020') or []
            issues.append(dict(key=i['key'], type=f['issuetype']['name'], summary=f.get('summary'), status=f['status']['name'],
                               status_cat=(f['status'].get('statusCategory') or {}).get('key'), parent=(f.get('parent') or {}).get('key'),
                               parent_summary=((f.get('parent') or {}).get('fields') or {}).get('summary'),
                               start=f.get('customfield_10015'), due=f.get('duedate'), target_start=f.get('customfield_10022'), target_end=f.get('customfield_10023'),
                               sprint=[dict(name=x.get('name'), state=x.get('state'), start=x.get('startDate'), end=x.get('endDate')) for x in sp] if isinstance(sp, list) else [],
                               assignee=(f.get('assignee') or {}).get('displayName'), labels=f.get('labels') or [], created=(f.get('created') or '')[:10],
                               resolved=(f.get('resolutiondate') or '')[:10], priority=(f.get('priority') or {}).get('name')))
        token = r.get('nextPageToken')
        if not token: break
    OUT.mkdir(exist_ok=True)
    (OUT / f'{key}.json').write_text(json.dumps(dict(project=key, fetched=datetime.datetime.now().isoformat(timespec='minutes'), issues=issues), ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{key}: {len(issues)} issues')
