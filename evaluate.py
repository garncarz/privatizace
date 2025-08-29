#!/usr/bin/env python

import asyncio

from evaluation import bots


async def run_all_evaluations():
    """Run all evaluation functions and collect results"""
    results = {}
    
    # Get all evaluation functions
    eval_functions = [getattr(bots, f) for f in dir(bots) if f.startswith('eval_')]
    
    print("Starting comprehensive bot evaluation...\n")
    print("=" * 60)
    
    for func in eval_functions:
        result = await func()
        # Use the description from the decorator if available
        if hasattr(func, '_description'):
            description = func._description
        else:
            description = func.__name__.replace('eval_', '').replace('_', ' ').title()
        results[description] = result
    
    print("=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    
    # Calculate overall statistics
    total_avg = sum(r['average'] for r in results.values()) / len(results)
    total_worst = sum(r['worst_case'] for r in results.values()) / len(results)
    
    print(f"Overall Average Performance: {total_avg:.1%}")
    print(f"Overall Worst Case Performance: {total_worst:.1%}")
    print()
    
    # Rank scenarios by performance
    ranked = sorted(results.items(), key=lambda x: x[1]['average'], reverse=True)
    
    print("Performance Ranking (by average):")
    for i, (desc, result) in enumerate(ranked, 1):
        print(f"{i:2d}. {desc:<45} {result['average']:.1%}")
    
    print("\nBot evaluation complete!")
    return results


def main():
    try:
        # Use the modern approach for Python 3.7+
        results = asyncio.run(run_all_evaluations())
    except AttributeError:
        # Fallback for older Python versions
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(run_all_evaluations())


if __name__ == '__main__':
    main()
