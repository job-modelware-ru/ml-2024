-- Get statistics of the count of comments for each channel grouped by country
SELECT
  c.country,
  ch.title AS channel_title,
  COUNT(co.id) AS comment_count
FROM
  channels ch
JOIN
  comments co ON ch.id = co.video_id
JOIN
  videos v ON co.video_id = v.id
JOIN
  channel_group cg ON ch.id = cg.channel_id
JOIN
  c c ON cg.user_id = c.id
GROUP BY
  c.country, ch.title
ORDER BY
  c.country, comment_count DESC;

-- Get statistics of the summary count of likes on comments for each video, grouped by time
SELECT
  v.id AS video_id,
  v.title AS video_title,
  DATE_TRUNC('day', co.publishedAt) AS comment_date,
  SUM(co.likeCount) AS total_likes_on_comments
FROM
  videos v
JOIN
  comments co ON v.id = co.video_id
GROUP BY
  video_id, video_title, comment_date
ORDER BY
  video_id, comment_date;

-- Get all comments from a group of channels
SELECT comments.*
FROM channels
JOIN videos ON channels.id = videos.channel_id
JOIN comments ON videos.id = comments.video_id
WHERE channels.id = your_channel_id;

-- Get all comments from channel
SELECT comments.*
FROM channel_group
JOIN channels ON channel_group.channel_id = channels.id
JOIN videos ON channels.id = videos.channel_id
JOIN comments ON videos.id = comments.video_id
WHERE channel_group.id = your_channel_group_id;

-- Get all comments from a video group
SELECT comments.*
FROM video_group
JOIN videos ON video_group.video_id = videos.id
JOIN comments ON videos.id = comments.video_id
WHERE video_group.id = your_video_group_id;
