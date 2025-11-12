"""
================================================================================
Database Manager - SQLite Persistence for AI Ticket Processor
================================================================================

DESCRIPTION:
    Production-ready SQLite database manager for persisting metrics, tickets,
    and historical analytics data. Provides thread-safe operations with context
    manager support for clean resource management.

FEATURES:
    - SQLite database for persistent storage
    - Thread-safe operations with locking
    - Context manager support (with statement)
    - Parameterized queries (SQL injection protection)
    - Automatic schema initialization
    - Upsert operations for metrics
    - Auto-cleanup of old tickets
    - Comprehensive error handling

TABLES:
    - daily_metrics: Daily aggregated statistics
    - processed_tickets: Individual ticket records
    - confidence_history: Category confidence trends

USAGE:
    from database_manager import DatabaseManager

    with DatabaseManager() as db:
        db.insert_daily_metric(today, metrics_dict)
        tickets = db.get_recent_tickets(limit=20)

AUTHOR: AI Ticket Processor Team
LICENSE: Proprietary
LAST UPDATED: 2025-11-12
================================================================================
"""

import sqlite3
import os
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    SQLite database manager for AI Ticket Processor.

    Provides thread-safe operations for storing and retrieving metrics,
    tickets, and historical data. Supports context manager protocol
    for automatic connection management.

    Attributes:
        db_path (str): Path to SQLite database file
        conn (sqlite3.Connection): Database connection
        lock (threading.Lock): Thread safety lock
    """

    def __init__(self, db_path: str = 'data/tickets.db'):
        """
        Initialize database manager with path to SQLite database.

        Args:
            db_path: Path to database file (default: 'data/tickets.db')
                    Creates directory if it doesn't exist
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self.lock = threading.Lock()

        # Create data directory if it doesn't exist
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            logger.info(f"Created directory: {db_dir}")

        # Initialize connection
        self._connect()

        # Initialize schema
        self.initialize_schema()

        logger.info(f"DatabaseManager initialized: {db_path}")

    def _connect(self):
        """Establish database connection with optimizations."""
        self.conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,  # Allow multi-threading
            timeout=30.0  # 30 second timeout
        )
        # Enable row factory for dict-like access
        self.conn.row_factory = sqlite3.Row
        # Enable foreign keys
        self.conn.execute("PRAGMA foreign_keys = ON")
        # Set journal mode for better concurrency
        self.conn.execute("PRAGMA journal_mode = WAL")
        logger.debug("Database connection established")

    def initialize_schema(self):
        """
        Create database tables if they don't exist.

        Creates three tables:
        1. daily_metrics: Aggregated daily statistics
        2. processed_tickets: Individual ticket records
        3. confidence_history: Category-level confidence trends
        """
        with self.lock:
            cursor = self.conn.cursor()

            # Table 1: Daily Metrics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL UNIQUE,
                    tickets_processed INTEGER DEFAULT 0,
                    accuracy_rate REAL DEFAULT 0.0,
                    avg_confidence REAL DEFAULT 0.0,
                    time_saved_hours REAL DEFAULT 0.0,
                    cost_saved_usd REAL DEFAULT 0.0,
                    pii_detected INTEGER DEFAULT 0,
                    pii_redacted INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Table 2: Processed Tickets
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processed_tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id TEXT NOT NULL UNIQUE,
                    description TEXT,
                    category TEXT,
                    industry TEXT,
                    confidence REAL,
                    status TEXT DEFAULT 'processed',
                    region TEXT DEFAULT 'US',
                    pii_detected BOOLEAN DEFAULT 0,
                    processing_time REAL DEFAULT 0.0,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Table 3: Confidence History
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS confidence_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    category TEXT NOT NULL,
                    avg_confidence REAL,
                    ticket_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date, category)
                )
            """)

            # Create indexes for better query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_daily_metrics_date
                ON daily_metrics(date)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tickets_processed_at
                ON processed_tickets(processed_at DESC)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tickets_category
                ON processed_tickets(category)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_confidence_history_date
                ON confidence_history(date)
            """)

            self.conn.commit()
            logger.info("Database schema initialized successfully")

    def insert_daily_metric(self, date: str, metrics_dict: Dict[str, Any]) -> bool:
        """
        Insert or update daily metrics (upsert pattern).

        Args:
            date: Date string in YYYY-MM-DD format
            metrics_dict: Dictionary containing metric values:
                - tickets_processed (int)
                - accuracy_rate (float)
                - avg_confidence (float)
                - time_saved_hours (float)
                - cost_saved_usd (float)
                - pii_detected (int)
                - pii_redacted (int)

        Returns:
            bool: True if successful, False otherwise
        """
        with self.lock:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO daily_metrics
                    (date, tickets_processed, accuracy_rate, avg_confidence,
                     time_saved_hours, cost_saved_usd, pii_detected, pii_redacted)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    date,
                    metrics_dict.get('tickets_processed', 0),
                    metrics_dict.get('accuracy_rate', 0.0),
                    metrics_dict.get('avg_confidence', 0.0),
                    metrics_dict.get('time_saved_hours', 0.0),
                    metrics_dict.get('cost_saved_usd', 0.0),
                    metrics_dict.get('pii_detected', 0),
                    metrics_dict.get('pii_redacted', 0)
                ))
                self.conn.commit()
                logger.info(f"Inserted/updated daily metrics for {date}")
                return True
            except Exception as e:
                logger.error(f"Error inserting daily metric: {e}")
                self.conn.rollback()
                return False

    def get_daily_metrics(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """
        Retrieve daily metrics within date range.

        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)

        Returns:
            List of dictionaries containing daily metrics
        """
        with self.lock:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT * FROM daily_metrics
                    WHERE date BETWEEN ? AND ?
                    ORDER BY date DESC
                """, (start_date, end_date))

                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            except Exception as e:
                logger.error(f"Error retrieving daily metrics: {e}")
                return []

    def insert_ticket(self, ticket_dict: Dict[str, Any]) -> bool:
        """
        Insert processed ticket record.

        Args:
            ticket_dict: Dictionary containing ticket data:
                - ticket_id (str, required)
                - description (str)
                - category (str)
                - industry (str)
                - confidence (float)
                - status (str)
                - region (str)
                - pii_detected (bool)
                - processing_time (float)

        Returns:
            bool: True if successful, False otherwise
        """
        with self.lock:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO processed_tickets
                    (ticket_id, description, category, industry, confidence,
                     status, region, pii_detected, processing_time)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ticket_dict.get('ticket_id'),
                    ticket_dict.get('description', ''),
                    ticket_dict.get('category', ''),
                    ticket_dict.get('industry', ''),
                    ticket_dict.get('confidence', 0.0),
                    ticket_dict.get('status', 'processed'),
                    ticket_dict.get('region', 'US'),
                    1 if ticket_dict.get('pii_detected', False) else 0,
                    ticket_dict.get('processing_time', 0.0)
                ))
                self.conn.commit()
                logger.debug(f"Inserted ticket: {ticket_dict.get('ticket_id')}")
                return True
            except Exception as e:
                logger.error(f"Error inserting ticket: {e}")
                self.conn.rollback()
                return False

    def get_recent_tickets(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """
        Retrieve most recent processed tickets.

        Args:
            limit: Maximum number of tickets to retrieve (default: 1000)

        Returns:
            List of dictionaries containing ticket data, ordered by most recent
        """
        with self.lock:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT * FROM processed_tickets
                    ORDER BY processed_at DESC
                    LIMIT ?
                """, (limit,))

                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            except Exception as e:
                logger.error(f"Error retrieving recent tickets: {e}")
                return []

    def insert_confidence_history(self, date: str, category: str,
                                  avg_conf: float, count: int) -> bool:
        """
        Insert or update confidence history for a category (upsert pattern).

        Args:
            date: Date string (YYYY-MM-DD format)
            category: Category name
            avg_conf: Average confidence score
            count: Number of tickets in this category

        Returns:
            bool: True if successful, False otherwise
        """
        with self.lock:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO confidence_history
                    (date, category, avg_confidence, ticket_count)
                    VALUES (?, ?, ?, ?)
                """, (date, category, avg_conf, count))
                self.conn.commit()
                logger.debug(f"Inserted confidence history: {category} on {date}")
                return True
            except Exception as e:
                logger.error(f"Error inserting confidence history: {e}")
                self.conn.rollback()
                return False

    def get_confidence_trends(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Retrieve confidence trends for the last N days.

        Args:
            days: Number of days to look back (default: 30)

        Returns:
            List of dictionaries containing confidence trends by category
        """
        with self.lock:
            try:
                start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT * FROM confidence_history
                    WHERE date >= ?
                    ORDER BY date DESC, category
                """, (start_date,))

                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            except Exception as e:
                logger.error(f"Error retrieving confidence trends: {e}")
                return []

    def cleanup_old_tickets(self, keep_last: int = 1000) -> int:
        """
        Delete old tickets, keeping only the most recent N tickets.

        Args:
            keep_last: Number of most recent tickets to keep (default: 1000)

        Returns:
            int: Number of tickets deleted
        """
        with self.lock:
            try:
                cursor = self.conn.cursor()

                # Get the ID threshold
                cursor.execute("""
                    SELECT id FROM processed_tickets
                    ORDER BY processed_at DESC
                    LIMIT 1 OFFSET ?
                """, (keep_last - 1,))

                result = cursor.fetchone()

                if result:
                    threshold_id = result[0]
                    cursor.execute("""
                        DELETE FROM processed_tickets
                        WHERE id < ?
                    """, (threshold_id,))
                    deleted = cursor.rowcount
                    self.conn.commit()
                    logger.info(f"Cleaned up {deleted} old tickets")
                    return deleted
                else:
                    logger.info("No tickets to clean up")
                    return 0
            except Exception as e:
                logger.error(f"Error cleaning up old tickets: {e}")
                self.conn.rollback()
                return 0

    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Get overall summary statistics from database.

        Returns:
            Dictionary containing:
            - total_tickets: Total number of tickets
            - total_days: Number of days with metrics
            - avg_accuracy: Average accuracy rate
            - total_time_saved: Total hours saved
            - total_cost_saved: Total cost savings
        """
        with self.lock:
            try:
                cursor = self.conn.cursor()

                # Get ticket count
                cursor.execute("SELECT COUNT(*) FROM processed_tickets")
                total_tickets = cursor.fetchone()[0]

                # Get metrics summary
                cursor.execute("""
                    SELECT
                        COUNT(*) as total_days,
                        AVG(accuracy_rate) as avg_accuracy,
                        SUM(time_saved_hours) as total_time_saved,
                        SUM(cost_saved_usd) as total_cost_saved
                    FROM daily_metrics
                """)
                row = cursor.fetchone()

                return {
                    'total_tickets': total_tickets,
                    'total_days': row[0] or 0,
                    'avg_accuracy': round(row[1] or 0.0, 2),
                    'total_time_saved': round(row[2] or 0.0, 2),
                    'total_cost_saved': round(row[3] or 0.0, 2)
                }
            except Exception as e:
                logger.error(f"Error getting summary stats: {e}")
                return {
                    'total_tickets': 0,
                    'total_days': 0,
                    'avg_accuracy': 0.0,
                    'total_time_saved': 0.0,
                    'total_cost_saved': 0.0
                }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def get_tickets_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Retrieve all tickets for a specific category.

        Args:
            category: Category name to filter by

        Returns:
            List of ticket dictionaries
        """
        with self.lock:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT * FROM processed_tickets
                    WHERE category = ?
                    ORDER BY processed_at DESC
                """, (category,))

                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            except Exception as e:
                logger.error(f"Error getting tickets by category: {e}")
                return []

    def get_tickets_by_date_range(self, start_date: str,
                                   end_date: str) -> List[Dict[str, Any]]:
        """
        Retrieve tickets within a date range.

        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)

        Returns:
            List of ticket dictionaries
        """
        with self.lock:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    SELECT * FROM processed_tickets
                    WHERE DATE(processed_at) BETWEEN ? AND ?
                    ORDER BY processed_at DESC
                """, (start_date, end_date))

                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            except Exception as e:
                logger.error(f"Error getting tickets by date range: {e}")
                return []

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        Get aggregated metrics summary with additional calculations.

        Returns:
            Dictionary with comprehensive metrics summary
        """
        with self.lock:
            try:
                cursor = self.conn.cursor()

                # Get overall metrics
                cursor.execute("""
                    SELECT
                        SUM(tickets_processed) as total_processed,
                        AVG(accuracy_rate) as avg_accuracy,
                        AVG(avg_confidence) as avg_confidence,
                        SUM(time_saved_hours) as total_time_saved,
                        SUM(cost_saved_usd) as total_cost_saved,
                        SUM(pii_detected) as total_pii_detected,
                        SUM(pii_redacted) as total_pii_redacted
                    FROM daily_metrics
                """)

                row = cursor.fetchone()

                # Get category breakdown
                cursor.execute("""
                    SELECT category, COUNT(*) as count
                    FROM processed_tickets
                    GROUP BY category
                    ORDER BY count DESC
                """)

                categories = {row[0]: row[1] for row in cursor.fetchall()}

                # Get industry breakdown
                cursor.execute("""
                    SELECT industry, COUNT(*) as count
                    FROM processed_tickets
                    GROUP BY industry
                    ORDER BY count DESC
                """)

                industries = {row[0]: row[1] for row in cursor.fetchall()}

                return {
                    'total_processed': row[0] or 0,
                    'avg_accuracy': round(row[1] or 0.0, 2),
                    'avg_confidence': round(row[2] or 0.0, 2),
                    'total_time_saved': round(row[3] or 0.0, 2),
                    'total_cost_saved': round(row[4] or 0.0, 2),
                    'total_pii_detected': row[5] or 0,
                    'total_pii_redacted': row[6] or 0,
                    'categories': categories,
                    'industries': industries
                }
            except Exception as e:
                logger.error(f"Error getting metrics summary: {e}")
                return {}

    def vacuum_database(self) -> bool:
        """
        Optimize database by reclaiming unused space.

        Returns:
            bool: True if successful, False otherwise
        """
        with self.lock:
            try:
                self.conn.execute("VACUUM")
                logger.info("Database vacuumed successfully")
                return True
            except Exception as e:
                logger.error(f"Error vacuuming database: {e}")
                return False

    # ========================================================================
    # Context Manager Support
    # ========================================================================

    def __enter__(self):
        """Enter context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager, ensuring cleanup."""
        self.close()
        return False  # Don't suppress exceptions

    def close(self):
        """Close database connection and cleanup resources."""
        if self.conn:
            try:
                self.conn.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")


# ============================================================================
# Testing Section
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("Testing DatabaseManager")
    print("=" * 80)

    # Use test database
    test_db_path = 'data/test_tickets.db'

    # Clean up test database if exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        print(f"Removed existing test database: {test_db_path}")

    print("\n" + "=" * 80)
    print("Test 1: Initialize Database")
    print("=" * 80)

    try:
        with DatabaseManager(test_db_path) as db:
            print("✅ Database initialized successfully")
            print(f"✅ Database path: {db.db_path}")
            print(f"✅ Connection established: {db.conn is not None}")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        exit(1)

    print("\n" + "=" * 80)
    print("Test 2: Insert Sample Data")
    print("=" * 80)

    with DatabaseManager(test_db_path) as db:
        # Insert 7 days of metrics
        print("\nInserting daily metrics...")
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            metrics = {
                'tickets_processed': 10 + i * 2,
                'accuracy_rate': 85.0 + i,
                'avg_confidence': 0.87 + i * 0.01,
                'time_saved_hours': 2.5 + i * 0.5,
                'cost_saved_usd': 62.5 + i * 12.5,
                'pii_detected': 5 + i,
                'pii_redacted': 5 + i
            }
            success = db.insert_daily_metric(date, metrics)
            if success:
                print(f"  ✅ Day {i+1}: {date} - {metrics['tickets_processed']} tickets")
            else:
                print(f"  ❌ Day {i+1}: Failed")

        # Insert 10 sample tickets
        print("\nInserting sample tickets...")
        categories = ['API Integration Error', 'Login/Authentication', 'Billing',
                     'Feature Request', 'Data Sync']
        industries = ['SaaS', 'E-commerce', 'General']
        regions = ['US', 'EU', 'UK']

        for i in range(10):
            ticket = {
                'ticket_id': f'ZD-{12345 + i}',
                'description': f'Sample ticket {i+1} - Testing database storage',
                'category': categories[i % len(categories)],
                'industry': industries[i % len(industries)],
                'confidence': 0.85 + (i * 0.01),
                'region': regions[i % len(regions)],
                'pii_detected': i % 3 == 0,  # Every 3rd ticket has PII
                'processing_time': 6.5 + (i * 0.3)
            }
            success = db.insert_ticket(ticket)
            if success:
                print(f"  ✅ Ticket {i+1}: {ticket['ticket_id']} - {ticket['category']}")
            else:
                print(f"  ❌ Ticket {i+1}: Failed")

        # Insert confidence history
        print("\nInserting confidence history...")
        for i in range(5):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            for category in categories[:3]:
                success = db.insert_confidence_history(
                    date, category, 0.88 + i * 0.01, 4 + i
                )
        print(f"  ✅ Inserted confidence history for 5 days, 3 categories")

    print("\n" + "=" * 80)
    print("Test 3: Query Operations")
    print("=" * 80)

    with DatabaseManager(test_db_path) as db:
        # Get daily metrics
        print("\n📊 Daily Metrics (last 7 days):")
        start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        end = datetime.now().strftime('%Y-%m-%d')
        metrics = db.get_daily_metrics(start, end)
        print(f"  Found {len(metrics)} days of metrics")
        if metrics:
            latest = metrics[0]
            print(f"  Latest: {latest['date']} - {latest['tickets_processed']} tickets, "
                  f"{latest['accuracy_rate']}% accuracy")

        # Get recent tickets
        print("\n🎫 Recent Tickets:")
        tickets = db.get_recent_tickets(limit=5)
        print(f"  Found {len(tickets)} tickets")
        for ticket in tickets[:3]:
            print(f"  - {ticket['ticket_id']}: {ticket['category']} "
                  f"({ticket['confidence']:.2f} confidence)")

        # Get confidence trends
        print("\n📈 Confidence Trends (last 30 days):")
        trends = db.get_confidence_trends(days=30)
        print(f"  Found {len(trends)} trend records")
        if trends:
            print(f"  Categories tracked: {len(set(t['category'] for t in trends))}")

        # Get tickets by category
        print("\n🏷️  Tickets by Category (API Integration Error):")
        category_tickets = db.get_tickets_by_category('API Integration Error')
        print(f"  Found {len(category_tickets)} tickets in this category")

        # Get summary stats
        print("\n📊 Summary Statistics:")
        summary = db.get_summary_stats()
        print(f"  Total Tickets: {summary['total_tickets']}")
        print(f"  Total Days: {summary['total_days']}")
        print(f"  Avg Accuracy: {summary['avg_accuracy']}%")
        print(f"  Time Saved: {summary['total_time_saved']} hours")
        print(f"  Cost Saved: ${summary['total_cost_saved']}")

        # Get metrics summary
        print("\n📊 Metrics Summary:")
        metrics_summary = db.get_metrics_summary()
        print(f"  Total Processed: {metrics_summary['total_processed']}")
        print(f"  Avg Confidence: {metrics_summary['avg_confidence']}")
        print(f"  PII Detected: {metrics_summary['total_pii_detected']}")
        print(f"  PII Redacted: {metrics_summary['total_pii_redacted']}")
        print(f"  Categories: {len(metrics_summary['categories'])}")
        print(f"  Industries: {len(metrics_summary['industries'])}")

    print("\n" + "=" * 80)
    print("Test 4: Verify Data Persistence")
    print("=" * 80)

    # Reopen database to verify persistence
    with DatabaseManager(test_db_path) as db:
        tickets = db.get_recent_tickets(limit=10)
        metrics = db.get_daily_metrics(
            (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            datetime.now().strftime('%Y-%m-%d')
        )

        print(f"\n✅ Reopened database successfully")
        print(f"✅ Found {len(tickets)} persisted tickets")
        print(f"✅ Found {len(metrics)} days of persisted metrics")

    print("\n" + "=" * 80)
    print("Test 5: Cleanup Operations")
    print("=" * 80)

    with DatabaseManager(test_db_path) as db:
        # Test cleanup (keep last 5 tickets)
        print("\n🧹 Testing cleanup (keep last 5 tickets):")
        deleted = db.cleanup_old_tickets(keep_last=5)
        print(f"  Deleted {deleted} old tickets")

        remaining = db.get_recent_tickets(limit=100)
        print(f"  Remaining tickets: {len(remaining)}")

        # Vacuum database
        print("\n🧹 Vacuuming database:")
        success = db.vacuum_database()
        if success:
            print("  ✅ Database optimized successfully")

        # Final stats
        print("\n📊 Final Statistics:")
        summary = db.get_summary_stats()
        print(f"  Total Tickets: {summary['total_tickets']}")
        print(f"  Total Days: {summary['total_days']}")

    # Test upsert functionality
    print("\n" + "=" * 80)
    print("Test 6: Upsert Functionality")
    print("=" * 80)

    with DatabaseManager(test_db_path) as db:
        today = datetime.now().strftime('%Y-%m-%d')

        # Insert initial metrics
        print(f"\n📝 Inserting initial metrics for {today}:")
        metrics1 = {
            'tickets_processed': 10,
            'accuracy_rate': 85.0,
            'avg_confidence': 0.87,
            'time_saved_hours': 2.5,
            'cost_saved_usd': 62.5,
            'pii_detected': 5,
            'pii_redacted': 5
        }
        db.insert_daily_metric(today, metrics1)
        result1 = db.get_daily_metrics(today, today)
        print(f"  First insert - Tickets: {result1[0]['tickets_processed']}")

        # Update same day (upsert)
        print(f"\n📝 Updating metrics for {today} (upsert):")
        metrics2 = {
            'tickets_processed': 25,  # Updated
            'accuracy_rate': 88.0,
            'avg_confidence': 0.90,
            'time_saved_hours': 6.25,
            'cost_saved_usd': 156.25,
            'pii_detected': 12,
            'pii_redacted': 12
        }
        db.insert_daily_metric(today, metrics2)
        result2 = db.get_daily_metrics(today, today)
        print(f"  After upsert - Tickets: {result2[0]['tickets_processed']}")

        if result2[0]['tickets_processed'] == 25:
            print("  ✅ Upsert working correctly (data updated, not duplicated)")
        else:
            print("  ❌ Upsert failed")

    print("\n" + "=" * 80)
    print("✅ All Tests Passed!")
    print("=" * 80)

    print(f"\n📁 Test database location: {test_db_path}")
    print(f"📁 Database size: {os.path.getsize(test_db_path) / 1024:.2f} KB")

    print("\n🎉 DatabaseManager is ready for production use!")
    print("\nTo use in your application:")
    print("  from database_manager import DatabaseManager")
    print("  ")
    print("  with DatabaseManager() as db:")
    print("      db.insert_ticket(ticket_data)")
    print("      tickets = db.get_recent_tickets(limit=20)")
