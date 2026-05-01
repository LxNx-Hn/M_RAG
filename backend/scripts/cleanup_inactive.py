"""
cleanup_inactive.py — Remove users inactive for 30+ days.

Usage:
    python scripts/cleanup_inactive.py --dry-run    # preview only
    python scripts/cleanup_inactive.py --execute    # actually delete

Protected accounts (safelist) are never deleted.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Allow running from backend/ or project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


SAFELIST_EMAILS = frozenset(
    {
        "runner@mrag.local",
    }
)

INACTIVE_DAYS = 30


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Remove inactive users")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--dry-run", action="store_true", help="Preview without deleting"
    )
    group.add_argument("--execute", action="store_true", help="Actually delete users")
    parser.add_argument(
        "--days",
        type=int,
        default=INACTIVE_DAYS,
        help=f"Inactivity threshold in days (default: {INACTIVE_DAYS})",
    )
    parser.add_argument(
        "--exclude-email",
        action="append",
        default=[],
        help="Additional email addresses to protect from deletion",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    safelist = SAFELIST_EMAILS | frozenset(args.exclude_email)
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)

    # Synchronous DB access for the cleanup script
    import sqlalchemy
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session as SASession

    from api.models import User

    db_url = "sqlite:///./mrag.db"
    engine = create_engine(db_url.replace("sqlite+aiosqlite", "sqlite"))

    with SASession(engine) as session:
        # Find inactive users:
        # - last_login_at is NULL and created_at < cutoff (never logged in)
        # - last_login_at < cutoff
        stmt = select(User).where(
            sqlalchemy.or_(
                sqlalchemy.and_(User.last_login_at.is_(None), User.created_at < cutoff),
                User.last_login_at < cutoff,
            )
        )
        users = session.execute(stmt).scalars().all()

        candidates = [u for u in users if u.email not in safelist]
        protected = [u for u in users if u.email in safelist]

        print(f"Cutoff date: {cutoff.isoformat()}")
        print(f"Total inactive users found: {len(users)}")
        print(f"Protected (safelist): {len(protected)}")
        print(f"Candidates for deletion: {len(candidates)}")
        print()

        if protected:
            print("Protected accounts (will NOT be deleted):")
            for u in protected:
                print(f"  - {u.email} (last_login: {u.last_login_at})")
            print()

        if not candidates:
            print("No users to delete.")
            return 0

        print("Users to delete:")
        for u in candidates:
            print(
                f"  - {u.email} (created: {u.created_at}, last_login: {u.last_login_at})"
            )

        if args.dry_run:
            print("\nDry run complete. No users were deleted.")
            return 0

        # Execute deletion
        print(f"\nDeleting {len(candidates)} users...")
        for u in candidates:
            session.delete(u)  # CASCADE handles related data
        session.commit()
        print("Done.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
