from app.database import connect


def list_tasks():
    with connect() as db:
        return [dict(row) for row in db.execute("SELECT * FROM tasks ORDER BY id")]


def get_task(task_id):
    with connect() as db:
        row = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return dict(row) if row else None


def create_task(title):
    with connect() as db:
        cursor = db.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
        return dict(db.execute("SELECT * FROM tasks WHERE id = ?", (cursor.lastrowid,)).fetchone())


def update_task(task_id, changes):
    # Field names originate from the validated schema, never directly from SQL input.
    with connect() as db:
        for field, value in changes.items():
            if field not in {"title", "done"}:
                raise ValueError("Unexpected field")
            db.execute(f"UPDATE tasks SET {field} = ? WHERE id = ?", (value, task_id))
        row = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return dict(row) if row else None


def delete_task(task_id):
    with connect() as db:
        return db.execute("DELETE FROM tasks WHERE id = ?", (task_id,)).rowcount > 0
