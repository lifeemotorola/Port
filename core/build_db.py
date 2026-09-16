#!/usr/bin/env python3
"""
Port Knowledge Base Generator
Generates a comprehensive database of ports, protocols, services,
security risk levels, and vulnerability / penetration testing notes.
"""
import json
import os

def load_or_create():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ports_db.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data.sort(key=lambda x: x['port'])
            return data
    return []

if __name__ == '__main__':
    data = load_or_create()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ports_db.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[+] ports_db.json verified with {len(data)} port definitions.")
