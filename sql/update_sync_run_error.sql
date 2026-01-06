UPDATE sync_runs SET status = 'error', error = ?, finished_at = ?
WHERE id = ?;
