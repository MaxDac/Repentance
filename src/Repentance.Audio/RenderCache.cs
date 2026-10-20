using System;
using System.Collections.Generic;

namespace Repentance;

/// <summary>
/// Decides which slow renders (the music tracks) to make and which to keep. Only <see cref="Capacity"/> results are
/// kept. When a new one arrives, the least recently used one is dropped, but never the <see cref="Pinned"/> one (the
/// track playing). Renders happen one at a time: <see cref="Request"/>ed keys go first, then the
/// <see cref="Prefetch"/>ed guesses. Not thread-safe: use it from one thread.
/// </summary>
public sealed class RenderCache<TKey, TValue> where TKey : struct
{
    private readonly Dictionary<TKey, TValue> _values = new();
    // least recently used first
    private readonly LinkedList<TKey> _usage = new();
    private readonly List<TKey> _requested = new();
    private readonly List<TKey> _prefetch = new();

    public RenderCache(int capacity)
    {
        if (capacity < 1) throw new ArgumentOutOfRangeException(nameof(capacity));
        Capacity = capacity;
    }

    public int Capacity { get; }

    /// <summary>Never evicted while set (the track playing).</summary>
    public TKey? Pinned { get; set; }

    /// <summary>The key being rendered, between <see cref="TryStartNext"/> and <see cref="Finish"/> or <see cref="Fail"/>.</summary>
    public TKey? Rendering { get; private set; }

    public int Count => _values.Count;

    public IReadOnlyCollection<TKey> Keys => _values.Keys;

    /// <summary>Keys waiting to render, in order.</summary>
    public IEnumerable<TKey> Queue
    {
        get
        {
            foreach (var key in _requested) yield return key;
            foreach (var key in _prefetch) yield return key;
        }
    }

    public bool Contains(TKey key) => _values.ContainsKey(key);

    /// <summary>The kept result, now counted as the most recently used.</summary>
    public bool TryGet(TKey key, out TValue value)
    {
        if (!_values.TryGetValue(key, out value!)) return false;
        Touch(key);
        return true;
    }

    /// <summary>Asks for a render as soon as possible: ahead of everything else still waiting.</summary>
    public void Request(TKey key)
    {
        _prefetch.Remove(key);
        if (_values.ContainsKey(key) || Same(Rendering, key)) return;
        _requested.Remove(key);
        _requested.Insert(0, key);
    }

    /// <summary>
    /// Replaces the earlier guesses with these keys, rendered after the requests. The list is cut short so that the
    /// guesses never push the pinned key or one another out of the cache. Guesses already kept count as just used.
    /// </summary>
    public void Prefetch(IEnumerable<TKey> keys)
    {
        _prefetch.Clear();
        var wanted = new List<TKey>();
        foreach (var key in keys)
            if (!wanted.Contains(key) && !Same(key, Pinned) && wanted.Count < Capacity - 1) wanted.Add(key);
        foreach (var key in wanted)
        {
            if (_values.ContainsKey(key)) Touch(key);
            else if (!Same(Rendering, key) && !_requested.Contains(key)) _prefetch.Add(key);
        }
    }

    /// <summary>Takes the next key to render, if any.</summary>
    public bool TryStartNext(out TKey key)
    {
        key = default;
        if (Rendering != null) return false;
        var list = _requested.Count > 0 ? _requested : _prefetch;
        if (list.Count == 0) return false;
        key = list[0];
        list.RemoveAt(0);
        Rendering = key;
        return true;
    }

    /// <summary>Keeps a finished render and returns the keys dropped to make room for it.</summary>
    public List<TKey> Finish(TKey key, TValue value)
    {
        if (Same(Rendering, key)) Rendering = null;
        _values[key] = value;
        Touch(key);
        var evicted = new List<TKey>();
        for (var node = _usage.First; node != null && _values.Count > Capacity;)
        {
            var next = node.Next;
            if (!node.Value.Equals(key) && !Same(node.Value, Pinned))
            {
                _values.Remove(node.Value);
                _usage.Remove(node);
                evicted.Add(node.Value);
            }
            node = next;
        }
        return evicted;
    }

    public void Fail(TKey key)
    {
        if (Same(Rendering, key)) Rendering = null;
    }

    /// <summary>Drops everything still waiting to render.</summary>
    public void ClearQueue()
    {
        _requested.Clear();
        _prefetch.Clear();
    }

    private void Touch(TKey key)
    {
        _usage.Remove(key);
        if (_values.ContainsKey(key)) _usage.AddLast(key);
    }

    private static bool Same(TKey? a, TKey? b) => Nullable.Equals(a, b);
}
