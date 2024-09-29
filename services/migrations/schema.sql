SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

-- *not* creating schema, since initdb creates it


--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS '';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: chat_completion; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chat_completion (
    id integer NOT NULL,
    prompt text NOT NULL,
    completion text NOT NULL,
    prompt_tokens integer NOT NULL,
    completion_tokens integer NOT NULL,
    cache_used boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    route_id integer NOT NULL,
    session_id integer NOT NULL,
    options character varying(255) NOT NULL
);


--
-- Name: chat_completion_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.chat_completion_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: chat_completion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.chat_completion_id_seq OWNED BY public.chat_completion.id;


--
-- Name: client; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.client (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    token character varying(255) NOT NULL
);


--
-- Name: client_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.client_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: client_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.client_id_seq OWNED BY public.client.id;


--
-- Name: interceptor_error; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.interceptor_error (
    id integer NOT NULL,
    request character varying(65535) NOT NULL,
    response character varying(65535) NOT NULL,
    http_code integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    session_id integer NOT NULL
);


--
-- Name: interceptor_error_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.interceptor_error_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: interceptor_error_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.interceptor_error_id_seq OWNED BY public.interceptor_error.id;


--
-- Name: llm_provider; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.llm_provider (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    protocol character varying(255) NOT NULL,
    token character varying(255),
    url character varying(255) NOT NULL
);


--
-- Name: llm_provider_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.llm_provider_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: llm_provider_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.llm_provider_id_seq OWNED BY public.llm_provider.id;


--
-- Name: route; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.route (
    id integer NOT NULL,
    from_client_id integer NOT NULL,
    from_model character varying(255) NOT NULL,
    to_provider_id integer NOT NULL,
    to_model character varying(255) NOT NULL,
    active boolean NOT NULL,
    enabled boolean NOT NULL
);


--
-- Name: route_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.route_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: route_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.route_id_seq OWNED BY public.route.id;


--
-- Name: schema_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.schema_migrations (
    version character varying(128) NOT NULL
);


--
-- Name: session; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.session (
    id integer NOT NULL,
    client_id integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    active_connections integer NOT NULL,
    failed_connections integer NOT NULL,
    total_connections integer NOT NULL
);


--
-- Name: session_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.session_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: session_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.session_id_seq OWNED BY public.session.id;


--
-- Name: text_embedding; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.text_embedding (
    id integer NOT NULL,
    prompt text NOT NULL,
    cache_used boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    route_id integer NOT NULL,
    session_id integer NOT NULL,
    prompt_tokens integer NOT NULL
);


--
-- Name: text_embedding_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.text_embedding_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: text_embedding_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.text_embedding_id_seq OWNED BY public.text_embedding.id;


--
-- Name: chat_completion id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_completion ALTER COLUMN id SET DEFAULT nextval('public.chat_completion_id_seq'::regclass);


--
-- Name: client id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client ALTER COLUMN id SET DEFAULT nextval('public.client_id_seq'::regclass);


--
-- Name: interceptor_error id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.interceptor_error ALTER COLUMN id SET DEFAULT nextval('public.interceptor_error_id_seq'::regclass);


--
-- Name: llm_provider id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.llm_provider ALTER COLUMN id SET DEFAULT nextval('public.llm_provider_id_seq'::regclass);


--
-- Name: route id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.route ALTER COLUMN id SET DEFAULT nextval('public.route_id_seq'::regclass);


--
-- Name: session id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.session ALTER COLUMN id SET DEFAULT nextval('public.session_id_seq'::regclass);


--
-- Name: text_embedding id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.text_embedding ALTER COLUMN id SET DEFAULT nextval('public.text_embedding_id_seq'::regclass);


--
-- Name: chat_completion chat_completion_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_completion
    ADD CONSTRAINT chat_completion_pkey PRIMARY KEY (id);


--
-- Name: client client_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.client
    ADD CONSTRAINT client_pkey PRIMARY KEY (id);


--
-- Name: interceptor_error interceptor_error_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.interceptor_error
    ADD CONSTRAINT interceptor_error_pkey PRIMARY KEY (id);


--
-- Name: llm_provider llm_provider_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.llm_provider
    ADD CONSTRAINT llm_provider_pkey PRIMARY KEY (id);


--
-- Name: route route_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.route
    ADD CONSTRAINT route_pkey PRIMARY KEY (id);


--
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.schema_migrations
    ADD CONSTRAINT schema_migrations_pkey PRIMARY KEY (version);


--
-- Name: session session_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.session
    ADD CONSTRAINT session_pkey PRIMARY KEY (id);


--
-- Name: text_embedding text_embedding_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.text_embedding
    ADD CONSTRAINT text_embedding_pkey PRIMARY KEY (id);


--
-- Name: chatcompletion_route_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX chatcompletion_route_id ON public.chat_completion USING btree (route_id);


--
-- Name: chatcompletion_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX chatcompletion_session_id ON public.chat_completion USING btree (session_id);


--
-- Name: client_name_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX client_name_idx ON public.client USING btree (name);


--
-- Name: interceptor_error_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX interceptor_error_session_id ON public.interceptor_error USING btree (session_id);


--
-- Name: route_client_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX route_client_id ON public.route USING btree (from_client_id);


--
-- Name: route_from_client_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX route_from_client_id ON public.route USING btree (from_client_id);


--
-- Name: route_to_provider_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX route_to_provider_id ON public.route USING btree (to_provider_id);


--
-- Name: session_client_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX session_client_id ON public.session USING btree (client_id);


--
-- Name: session_client_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX session_client_id_idx ON public.session USING btree (client_id, updated_at, active_connections);


--
-- Name: textembedding_route_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX textembedding_route_id ON public.text_embedding USING btree (route_id);


--
-- Name: textembedding_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX textembedding_session_id ON public.text_embedding USING btree (session_id);


--
-- Name: textembeddings_route_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX textembeddings_route_id ON public.text_embedding USING btree (route_id);


--
-- Name: textembeddings_session_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX textembeddings_session_id ON public.text_embedding USING btree (session_id);


--
-- Name: chat_completion chat_completion_route_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_completion
    ADD CONSTRAINT chat_completion_route_id_fkey FOREIGN KEY (route_id) REFERENCES public.route(id);


--
-- Name: chat_completion chat_completion_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chat_completion
    ADD CONSTRAINT chat_completion_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.session(id);


--
-- Name: interceptor_error interceptor_error_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.interceptor_error
    ADD CONSTRAINT interceptor_error_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.session(id);


--
-- Name: route route_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.route
    ADD CONSTRAINT route_client_id_fkey FOREIGN KEY (from_client_id) REFERENCES public.client(id);


--
-- Name: route route_to_provider_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.route
    ADD CONSTRAINT route_to_provider_id_fkey FOREIGN KEY (to_provider_id) REFERENCES public.llm_provider(id);


--
-- Name: session session_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.session
    ADD CONSTRAINT session_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.client(id);


--
-- Name: text_embedding text_embedding_route_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.text_embedding
    ADD CONSTRAINT text_embedding_route_id_fkey FOREIGN KEY (route_id) REFERENCES public.route(id);


--
-- Name: text_embedding text_embedding_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.text_embedding
    ADD CONSTRAINT text_embedding_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.session(id);


--
-- PostgreSQL database dump complete
--


--
-- Dbmate schema migrations
--

INSERT INTO public.schema_migrations (version) VALUES
    ('20240630175424'),
    ('20240630175934'),
    ('20240729002827'),
    ('20240729204550'),
    ('20240730045430'),
    ('20240914042853'),
    ('20240914053232'),
    ('20240914105237'),
    ('20240915082526');
