"""Multi-player game simulator: 2 dice, bounce back past 300, action squares.

Metric: rounds until the first player reaches 300 (a round = every player gets a turn).

Action squares
  turbo   : extra turn immediately (can chain)
  block   : fixed square. First player to land on it activates it against everyone else.
            Another player passing through / landing on an active block stops there and
            skips their next turn; the block is then cleared (can be re-activated later).
  energy  : on the next player's turn, that player rolls, YOU move by their roll and they stay.
  swap    : swap places with a player above you ('nearest' = closest above,
            'dice' = random among all players above you).
"""
import json, random, statistics, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
N = 300

def load_jumps(path=os.path.join(HERE, 'layout.json'), edits=None):
    L = json.load(open(path))['elems']
    S = {e['hi']: e['lo'] for e in L if e['kind'] == 'S'}
    La = {e['lo']: e['hi'] for e in L if e['kind'] == 'L'}
    if edits:
        for h in edits.get('remove_snakes', []): S.pop(h, None)
        S.update(edits.get('add_snakes', {}))
    J = {**S, **La}
    return J, S, La

def place_actions(J, per_type=4, seed=11, types=('turbo', 'block', 'energy', 'swap'), counts=None):
    """Spread action squares evenly over the board, away from snake/ladder ends."""
    rnd = random.Random(seed)
    ends = set(J) | set(J.values())
    banned = ends | {1, N} | set(range(290, N + 1))
    free = [s for s in range(2, 290) if s not in banned and not any(abs(s - e) <= 1 for e in ends)]
    acts = {}
    counts = counts or {t: per_type for t in types}
    for t, n in counts.items():
        for k in range(n):
            lo, hi = 2 + k * 288 // n, 2 + (k + 1) * 288 // n
            cands = [s for s in free if lo <= s < hi and s not in acts and not any(abs(s - a) <= 2 for a in acts)]
            if cands:
                acts[rnd.choice(cands)] = t
    return acts

def play(J, acts, players=3, swap_rule='nearest', rnd=random, ev=None):
    ev = ev if ev is not None else {}
    def bump(k, v=1): ev[k] = ev.get(k, 0) + v
    pos = [1] * players
    skip = [False] * players
    block_owner = {}           # square -> owner index (active blocks)
    pending_pull = None        # player who will be moved by the next player's roll
    rounds = 0
    def roll(): return rnd.randint(1, 6) + rnd.randint(1, 6)

    def move(p, steps):
        """Move player p by steps; returns final square (blocks, bounce, snakes/ladders)."""
        cur = pos[p]
        path = []; x = cur; d = 1
        for _ in range(steps):
            if x == N: d = -1
            x += d; path.append(x)
        for sq in path:
            if sq in block_owner and block_owner[sq] != p:
                del block_owner[sq]
                skip[p] = True; bump('stuck')
                return sq, True
        dest = path[-1] if path else cur
        if dest in J: bump('snake' if J[dest] < dest else 'ladder')
        dest = J.get(dest, dest)
        return dest, False

    def take_turn(p, depth=0):
        nonlocal pending_pull
        r = roll(); bump('turns')
        if pending_pull is not None and pending_pull != p:
            q = pending_pull; pending_pull = None; bump('pull'); bump('pull_steps', r)
            dest, stuck = move(q, r)
            pos[q] = dest
            return q if pos[q] == N else None
        dest, stuck = move(p, r)
        pos[p] = dest
        if pos[p] == N: return p
        if stuck: return None
        a = acts.get(dest)
        if a: bump('land_' + a)
        if a == 'turbo' and depth < 10:
            return take_turn(p, depth + 1)
        if a == 'block' and dest not in block_owner:
            block_owner[dest] = p
        if a == 'energy':
            pending_pull = p
        if a == 'swap':
            above = [o for o in range(players) if o != p and pos[o] > pos[p]]
            if above:
                if swap_rule == 'nearest':
                    o = min(above, key=lambda o: pos[o])
                else:
                    o = rnd.choice(above)
                bump('swap_gain', pos[o] - pos[p]); bump('swaps')
                pos[p], pos[o] = pos[o], pos[p]
        return None

    while rounds < 2000:
        rounds += 1
        for p in range(players):
            if skip[p]:
                skip[p] = False; continue
            w = take_turn(p)
            if w is not None:
                return rounds
    return rounds

def stats(J, acts, players, swap_rule='nearest', games=20000, seed=1):
    rnd = random.Random(seed)
    r = [play(J, acts, players, swap_rule, rnd) for _ in range(games)]
    r.sort()
    return dict(mean=round(statistics.mean(r), 1), median=statistics.median(r),
                p10=r[len(r)//10], p90=r[9*len(r)//10])

if __name__ == '__main__':
    pass
