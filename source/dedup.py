def dedup_records(rows: list[dict]) -> tuple[list[dict], int]:
        seen, uniq, dropped = set(), [], 0
        for r in rows:
            k = r.get("job_key")
            if k in seen:
                dropped += 1
                continue
            seen.add(k); uniq.append(r)
        return uniq, dropped