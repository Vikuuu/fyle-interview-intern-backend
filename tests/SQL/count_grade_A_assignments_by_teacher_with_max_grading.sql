-- Write query to find the number of grade A's given by the teacher who has graded the most assignments
SELECT count(*) as grade_A
    FROM assignments
    WHERE grade = 'A'
    AND teacher_id = (
        SELECT count(*)
            FROM assignments
            WHERE state = 'GRADED'
            GROUP BY teacher_id
            ORDER BY count(*) DESC
            LIMIT 1
        )
    ORDER BY count(*) DESC
LIMIT 1;
