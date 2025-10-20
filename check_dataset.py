#!/usr/bin/env python3
"""
Check the Vietnam travel dataset for specific content
"""
import json

def check_dataset():
    with open('vietnam_travel_dataset.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Total items in dataset: {len(data)}")
    
    # Check for zoos
    zoo_items = [item for item in data if 
                 'zoo' in item.get('name', '').lower() or 
                 'zoo' in item.get('description', '').lower() or
                 any('zoo' in str(tag).lower() for tag in item.get('tags', []))]
    
    print(f"\nZoo-related items: {len(zoo_items)}")
    for item in zoo_items[:5]:
        print(f"- {item['name']} ({item.get('type', 'Unknown')})")
        if item.get('description'):
            print(f"  Description: {item['description'][:100]}...")
    
    # Check types
    types = {}
    for item in data:
        item_type = item.get('type', 'Unknown')
        types[item_type] = types.get(item_type, 0) + 1
    
    print(f"\nItem types:")
    for item_type, count in sorted(types.items()):
        print(f"- {item_type}: {count}")
    
    # Check for Hanoi items
    hanoi_items = [item for item in data if 
                   'hanoi' in item.get('name', '').lower() or 
                   'hanoi' in item.get('city', '').lower() or
                   'hanoi' in item.get('description', '').lower()]
    
    print(f"\nHanoi-related items: {len(hanoi_items)}")
    for item in hanoi_items[:10]:
        print(f"- {item['name']} ({item.get('type', 'Unknown')}) - {item.get('city', '')}")
    
    # Sample a few items
    print(f"\nSample items:")
    for i, item in enumerate(data[:3]):
        print(f"{i+1}. {item['name']} ({item.get('type', 'Unknown')})")
        print(f"   City: {item.get('city', item.get('region', 'N/A'))}")
        print(f"   Tags: {item.get('tags', [])}")
        if item.get('description'):
            print(f"   Description: {item['description'][:150]}...")
        print()

if __name__ == "__main__":
    check_dataset()