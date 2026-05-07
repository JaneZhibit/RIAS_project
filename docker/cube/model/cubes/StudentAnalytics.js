cube(`StudentAnalytics`, {
  sql: `SELECT day, faculty, group_name, student_id, avg_grade, engagement_score FROM analytics_student_daily`,

  dimensions: {
    day: {
      sql: `day`,
      type: `time`,
    },
    faculty: {
      sql: `faculty`,
      type: `string`,
    },
    groupName: {
      sql: `group_name`,
      type: `string`,
    },
    studentId: {
      sql: `student_id`,
      type: `string`,
    },
  },

  measures: {
    studentCount: {
      type: `count`,
    },
    avgGrade: {
      sql: `avg_grade`,
      type: `avg`,
    },
    avgEngagement: {
      sql: `engagement_score`,
      type: `avg`,
    },
  },
});

cube(`CampusOccupancy`, {
  sql: `SELECT window_start, building_id, people FROM campus_occupancy_5m`,

  dimensions: {
    windowStart: {
      sql: `window_start`,
      type: `time`,
    },
    buildingId: {
      sql: `building_id`,
      type: `string`,
    },
  },

  measures: {
    peopleMax: {
      sql: `people`,
      type: `max`,
    },
    peopleAvg: {
      sql: `people`,
      type: `avg`,
    },
  },
});
