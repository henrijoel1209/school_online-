from django.db import migrations


class Migration(migrations.Migration):
    """Cette migration crée les tables pour les tests"""

    dependencies = [
        ('student', '0010_noop'),
    ]

    operations = [
        migrations.RunSQL(
            # Forward SQL - Crée les tables si elles n'existent pas
            """
            CREATE TABLE IF NOT EXISTS "student_courseprogress" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "started_at" datetime NOT NULL,
                "last_accessed" datetime NOT NULL,
                "completion_date" datetime NULL,
                "status" bool NOT NULL,
                "course_id" integer NOT NULL REFERENCES "school_cours" ("id") DEFERRABLE INITIALLY DEFERRED,
                "student_id" integer NOT NULL REFERENCES "student_student" ("id") DEFERRABLE INITIALLY DEFERRED
            );
            
            CREATE TABLE IF NOT EXISTS "student_chapterprogress" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "completed" bool NOT NULL,
                "time_spent" text NOT NULL,
                "last_position" integer unsigned NOT NULL,
                "completion_date" datetime NULL,
                "date_add" datetime NOT NULL,
                "date_update" datetime NOT NULL,
                "status" bool NOT NULL,
                "chapter_id" integer NOT NULL REFERENCES "school_chapitre" ("id") DEFERRABLE INITIALLY DEFERRED,
                "course_progress_id" integer NOT NULL REFERENCES "student_courseprogress" ("id") DEFERRABLE INITIALLY DEFERRED
            );
            
            CREATE TABLE IF NOT EXISTS "student_learningactivity" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "activity_type" varchar(50) NOT NULL,
                "timestamp" datetime NOT NULL,
                "details" text NULL,
                "status" bool NOT NULL,
                "chapter_id" integer NULL REFERENCES "school_chapitre" ("id") DEFERRABLE INITIALLY DEFERRED,
                "course_id" integer NOT NULL REFERENCES "school_cours" ("id") DEFERRABLE INITIALLY DEFERRED,
                "student_id" integer NOT NULL REFERENCES "student_student" ("id") DEFERRABLE INITIALLY DEFERRED
            );
            
            CREATE UNIQUE INDEX IF NOT EXISTS "student_courseprogress_student_id_course_id_unique" ON "student_courseprogress" ("student_id", "course_id");
            CREATE INDEX IF NOT EXISTS "student_courseprogress_course_id" ON "student_courseprogress" ("course_id");
            CREATE INDEX IF NOT EXISTS "student_courseprogress_student_id" ON "student_courseprogress" ("student_id");
            
            CREATE UNIQUE INDEX IF NOT EXISTS "student_chapterprogress_course_progress_id_chapter_id_unique" ON "student_chapterprogress" ("course_progress_id", "chapter_id");
            CREATE INDEX IF NOT EXISTS "student_chapterprogress_chapter_id" ON "student_chapterprogress" ("chapter_id");
            CREATE INDEX IF NOT EXISTS "student_chapterprogress_course_progress_id" ON "student_chapterprogress" ("course_progress_id");
            
            CREATE INDEX IF NOT EXISTS "student_learningactivity_chapter_id" ON "student_learningactivity" ("chapter_id");
            CREATE INDEX IF NOT EXISTS "student_learningactivity_course_id" ON "student_learningactivity" ("course_id");
            CREATE INDEX IF NOT EXISTS "student_learningactivity_student_id" ON "student_learningactivity" ("student_id");
            """,
            # Reverse SQL - Supprime les tables
            """
            DROP TABLE IF EXISTS student_learningactivity;
            DROP TABLE IF EXISTS student_chapterprogress;
            DROP TABLE IF EXISTS student_courseprogress;
            """
        ),
    ]
