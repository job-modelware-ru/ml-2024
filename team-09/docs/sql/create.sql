BEGIN;


CREATE TABLE IF NOT EXISTS public.api_keys
(
    id integer NOT NULL,
    remaining_quota integer,
    api_key text,
    mail text,
    last_reset timestamp without time zone,
    CONSTRAINT api_keys_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.calculation_results
(
    id integer NOT NULL,
    result text,
    user_id integer,
    CONSTRAINT calculation_results_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.channel_group
(
    id integer NOT NULL,
    title text,
    channel_id integer,
    user_id integer,
    CONSTRAINT channel_group_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.channels
(
    id integer NOT NULL,
    country text,
    description text,
    publishedat timestamp without time zone,
    subscribercount integer,
    title text,
    videocount integer,
    viewcount integer,
    CONSTRAINT channels_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.comments
(
    id integer NOT NULL,
    video_id integer,
    originaltext text,
    authordisplayname text,
    authorchannelid integer,
    likecount integer,
    publishedat timestamp without time zone,
    updatedat timestamp without time zone,
    totalreplycount integer,
    CONSTRAINT comments_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.keywords
(
    id integer NOT NULL,
    channel_id integer,
    keyword text,
    CONSTRAINT keywords_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.replies
(
    id integer NOT NULL,
    comment_id integer,
    reply_comment_id integer,
    CONSTRAINT replies_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.requests
(
    id integer NOT NULL,
    type integer,
    progress integer,
    date_completion timestamp without time zone,
    data text,
    user_id integer,
    CONSTRAINT requests_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.tags
(
    id integer NOT NULL,
    video_id integer,
    tag text,
    CONSTRAINT tags_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.users
(
    id integer NOT NULL,
    email text,
    login text,
    CONSTRAINT users_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.video_categories
(
    id integer NOT NULL,
    video_id integer,
    title text,
    CONSTRAINT video_categories_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.video_group
(
    id integer NOT NULL,
    title text,
    video_id integer,
    user_id integer,
    CONSTRAINT video_group_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.videos
(
    id integer NOT NULL,
    channel_id integer,
    description text,
    duration timestamp without time zone,
    likecount integer,
    publishedat timestamp without time zone,
    title text,
    viewcount integer,
    commentcount integer,
    language text,
    CONSTRAINT videos_pkey PRIMARY KEY (id)
);

ALTER TABLE IF EXISTS public.calculation_results
    ADD CONSTRAINT calculation_results_user_id_fkey FOREIGN KEY (user_id)
    REFERENCES public.users (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.channel_group
    ADD CONSTRAINT channel_group_channel_id_fkey FOREIGN KEY (channel_id)
    REFERENCES public.channels (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.channel_group
    ADD CONSTRAINT channel_group_user_id_fkey FOREIGN KEY (user_id)
    REFERENCES public.users (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.comments
    ADD CONSTRAINT comments_video_id_fkey FOREIGN KEY (video_id)
    REFERENCES public.videos (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.keywords
    ADD CONSTRAINT keywords_channel_id_fkey FOREIGN KEY (channel_id)
    REFERENCES public.channels (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.replies
    ADD CONSTRAINT replies_comment_id_fkey FOREIGN KEY (comment_id)
    REFERENCES public.comments (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.replies
    ADD CONSTRAINT replies_reply_comment_id_fkey FOREIGN KEY (reply_comment_id)
    REFERENCES public.comments (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.requests
    ADD CONSTRAINT requests_user_id_fkey FOREIGN KEY (user_id)
    REFERENCES public.users (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.tags
    ADD CONSTRAINT tags_video_id_fkey FOREIGN KEY (video_id)
    REFERENCES public.videos (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.video_categories
    ADD CONSTRAINT video_categories_video_id_fkey FOREIGN KEY (video_id)
    REFERENCES public.videos (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.video_group
    ADD CONSTRAINT video_group_user_id_fkey FOREIGN KEY (user_id)
    REFERENCES public.users (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.video_group
    ADD CONSTRAINT video_group_video_id_fkey FOREIGN KEY (video_id)
    REFERENCES public.videos (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;


ALTER TABLE IF EXISTS public.videos
    ADD CONSTRAINT videos_channel_id_fkey FOREIGN KEY (channel_id)
    REFERENCES public.channels (id) MATCH SIMPLE
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

END;