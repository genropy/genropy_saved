--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

--
-- Name: adm; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA adm;


ALTER SCHEMA adm OWNER TO postgres;

--
-- Name: genrotit; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA genrotit;


ALTER SCHEMA genrotit OWNER TO postgres;

--
-- Name: glbl; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA glbl;


ALTER SCHEMA glbl OWNER TO postgres;

--
-- Name: sys; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA sys;


ALTER SCHEMA sys OWNER TO postgres;

--
-- Name: test15; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA test15;


ALTER SCHEMA test15 OWNER TO postgres;

SET search_path = adm, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: adm_audit; Type: TABLE; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE TABLE adm_audit (
    id character(22) NOT NULL,
    __ins_ts timestamp without time zone,
    __del_ts timestamp without time zone,
    __mod_ts timestamp without time zone,
    tablename text,
    event character(1),
    username text,
    record_pkey text,
    version bigint,
    data text,
    transaction_id text
);


ALTER TABLE adm.adm_audit OWNER TO postgres;

--
-- Name: adm_authorization; Type: TABLE; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE TABLE adm_authorization (
    __ins_ts timestamp without time zone,
    __del_ts timestamp without time zone,
    __mod_ts timestamp without time zone,
    code character varying(8) NOT NULL,
    user_id character(22),
    use_ts timestamp without time zone,
    used_by character varying(32),
    note text,
    remaining_usages bigint,
    expiry_date date
);


ALTER TABLE adm.adm_authorization OWNER TO postgres;

--
-- Name: adm_connection; Type: TABLE; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE TABLE adm_connection (
    id character(22) NOT NULL,
    userid character varying(32),
    username character varying(32),
    ip character varying(15),
    start_ts timestamp without time zone,
    end_ts timestamp without time zone,
    end_reason character varying(12),
    user_agent text
);


ALTER TABLE adm.adm_connection OWNER TO postgres;

--
-- Name: adm_counter; Type: TABLE; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE TABLE adm_counter (
    __ins_ts timestamp without time zone,
    __del_ts timestamp without time zone,
    __mod_ts timestamp without time zone,
    codekey character varying(32) NOT NULL,
    code character varying(12),
    pkg character varying(12),
    name text,
    counter bigint,
    last_used date,
    holes text
);


ALTER TABLE adm.adm_counter OWNER TO postgres;

--
-- Name: adm_datacatalog; Type: TABLE; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE TABLE adm_datacatalog (
    id character(22) NOT NULL,
    __ins_ts timestamp without time zone,
    __del_ts timestamp without time zone,
    __mod_ts timestamp without time zone,
    code text,
    description text,
    child_code text,
    parent_code text,
    level text,
    rec_type text,
    dtype text,
    name_long text,
    name_short text,
    format text,
    options text,
    maxvalue text,
    minvalue text,
    dflt text,
    tip text,
    purpose text,
    ext_ref text,
    related_to text,
    pkg text,
    pkey_field text,
    field_size text,
    tbl text,
    fld text,
    comment text,
    name_full text,
    datacatalog_path text,
    dbkey text
);


ALTER TABLE adm.adm_datacatalog OWNER TO postgres;

--
-- Name: adm_doctemplate; Type: TABLE; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE TABLE adm_doctemplate (
    id character(22) NOT NULL,
    __ins_ts timestamp without time zone,
    __del_ts timestamp without time zone,
    __mod_ts timestamp without time zone,
    name text,
    content text,
    templatebag text,
    metadata text,
    varsbag text,
    username text,
    version text,
    locale text,
    maintable text,
    resource_name text
);


ALTER TABLE adm.adm_doctemplate OWNER TO postgres;

--
-- Name: adm_htag; Type: TABLE; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE TABLE adm_htag (
    id character(22) NOT NULL,
    __ins_ts timestamp without time zone,
    __del_ts timestamp without time zone,
    __mod_ts timestamp without time zone,
    code text,
    description text,
    child_code text,
    parent_code text,
    level text,
    rec_type text,
    isreserved boolean,
    note text
);


ALTER TABLE adm.adm_htag OWNER TO postgres;

--
-- Name: adm_htmltemplate; Type: TABLE; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE TABLE adm_htmltemplate (
    id character(22) NOT NULL,
    __ins_ts timestamp without time zone,
    __del_ts timestamp without time zone,
    __mod_ts timestamp without time zone,
    name text,
    username text,
    version text,
    data text
);


ALTER TABLE adm.adm_htmltemplate OWNER TO postgres;

--
-- Name: adm_menu; Type: TABLE; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE TABLE adm_menu (
    id character(22) NOT NULL,
    __ins_ts timestamp without time zone,
    __del_ts timestamp without time zone,
    __mod_ts timestamp without time zone,
    __rec_md5 text,
    code text,
    label text,
    basepath text,
    tags text,
    file text,
    description text,
    parameters text,
    "position" text,
    _class text,
    _style text
);


ALTER TABLE adm.adm_menu OWNER TO postgres;

--
-- Name: adm_permission; Type: TABLE; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE TABLE adm_permission (
    id character(22) NOT NULL,
    __ins_ts timestamp without time zone,
    __del_ts timestamp without time zone,
    __mod_ts timestamp without time zone,
    datacatalog_id character(22),
    tag_id text,
    view_read boolean,
    view_add boolean,
    view_del boolean,
    form_read boolean,
    form_add boolean,
    form_del boolean,
    form_upd boolean,
    column_read boolean,
    column_upd boolean
);


ALTER TABLE adm.adm_permission OWNER TO postgres;

--
-- Name: adm_preference; Type: TABLE; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE TABLE adm_preference (
    __ins_ts timestamp without time zone,
    __del_ts timestamp without time zone,
    __mod_ts timestamp without time zone,
    code character(12) NOT NULL,
    data text
);


ALTER TABLE adm.adm_preference OWNER TO postgres;

--
-- Name: adm_record_tag; Type: TABLE; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE TABLE adm_record_tag (
    id character(22) NOT NULL,
    __ins_ts timestamp without time zone,
    __del_ts timestamp without time zone,
    __mod_ts timestamp without time zone,
    tablename text,
    tag text,
    description text
);


ALTER TABLE adm.adm_record_tag OWNER TO postgres;

--
-- Name: adm_served_page; Type: TABLE; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE TABLE adm_served_page (
    page_id character(22) NOT NULL,
    pagename text,
    connection_id character(22),
    start_ts timestamp without time zone,
    end_ts timestamp without time zone,
    end_reason character varying(12)
);


ALTER TABLE adm.adm_served_page OWNER TO postgres;

--
-- Name: adm_tag; Type: TABLE; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE TABLE adm_tag (
    id character(22) NOT NULL,
    __ins_ts timestamp without time zone,
    __del_ts timestamp without time zone,
    __mod_ts timestamp without time zone,
    __rec_md5 text,
    tagname character varying(32),
    isreserved boolean,
    description text
);


ALTER TABLE adm.adm_tag OWNER TO postgres;

--
-- Name: adm_user; Type: TABLE; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE TABLE adm_user (
    id character(22) NOT NULL,
    __ins_ts timestamp without time zone,
    __del_ts timestamp without time zone,
    __mod_ts timestamp without time zone,
    __rec_md5 text,
    username character varying(32),
    email text,
    firstname character varying(32),
    lastname character varying(32),
    registration_date date,
    auth_tags text,
    status character(4),
    md5pwd character varying(65),
    locale character varying(12),
    preferences text,
    avatar_rootpage text
);


ALTER TABLE adm.adm_user OWNER TO postgres;

--
-- Name: adm_user_tag; Type: TABLE; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE TABLE adm_user_tag (
    id character(22) NOT NULL,
    __ins_ts timestamp without time zone,
    __del_ts timestamp without time zone,
    __mod_ts timestamp without time zone,
    user_id character(22),
    tag_id character(22)
);


ALTER TABLE adm.adm_user_tag OWNER TO postgres;

--
-- Name: adm_userobject; Type: TABLE; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE TABLE adm_userobject (
    id character(22) NOT NULL,
    __ins_ts timestamp without time zone,
    __del_ts timestamp without time zone,
    __mod_ts timestamp without time zone,
    code text,
    objtype text,
    pkg text,
    tbl text,
    userid text,
    description text,
    notes text,
    data text,
    authtags text,
    private boolean,
    quicklist boolean,
    flags text
);


ALTER TABLE adm.adm_userobject OWNER TO postgres;

SET search_path = genrotit, pg_catalog;

--
-- Name: genrotit_area_geografica; Type: TABLE; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE TABLE genrotit_area_geografica (
    id character(22) DEFAULT NULL::bpchar NOT NULL,
    __ins_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __del_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __mod_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    codice text,
    descrizione text,
    valuta_codice text
);


ALTER TABLE genrotit.genrotit_area_geografica OWNER TO postgres;

--
-- Name: genrotit_banca; Type: TABLE; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE TABLE genrotit_banca (
    id character(22) DEFAULT NULL::bpchar NOT NULL,
    __ins_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __del_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __mod_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    codice text,
    descrizione character varying(30) DEFAULT NULL::character varying,
    nome text,
    indirizzo text,
    cap text,
    localita text
);


ALTER TABLE genrotit.genrotit_banca OWNER TO postgres;

--
-- Name: genrotit_campo; Type: TABLE; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE TABLE genrotit_campo (
    id character(22) DEFAULT NULL::bpchar NOT NULL,
    __ins_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __del_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __mod_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    codice text,
    descrizione text,
    tipo_campo text,
    valori_ammessi text,
    classificazione text
);


ALTER TABLE genrotit.genrotit_campo OWNER TO postgres;

--
-- Name: genrotit_counter; Type: TABLE; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE TABLE genrotit_counter (
    __ins_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __del_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __mod_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    codekey character varying(32) DEFAULT NULL::character varying NOT NULL,
    code character varying(12) DEFAULT NULL::character varying,
    pkg character varying(12) DEFAULT NULL::character varying,
    name text,
    counter bigint,
    last_used date,
    holes text
);


ALTER TABLE genrotit.genrotit_counter OWNER TO postgres;

--
-- Name: genrotit_emittente; Type: TABLE; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE TABLE genrotit_emittente (
    id character(22) DEFAULT NULL::bpchar NOT NULL,
    __ins_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __del_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __mod_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    codice text,
    descrizione text,
    area_geografica_id text
);


ALTER TABLE genrotit.genrotit_emittente OWNER TO postgres;

--
-- Name: genrotit_gestione; Type: TABLE; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE TABLE genrotit_gestione (
    id character(22) DEFAULT NULL::bpchar NOT NULL,
    __ins_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __del_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __mod_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    banca_id character(22) DEFAULT NULL::bpchar,
    codice text,
    descrizione text,
    conto text,
    valuta_codice text
);


ALTER TABLE genrotit.genrotit_gestione OWNER TO postgres;

--
-- Name: genrotit_h_tipo_titolo; Type: TABLE; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE TABLE genrotit_h_tipo_titolo (
    id character(22) DEFAULT NULL::bpchar NOT NULL,
    __ins_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __del_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __mod_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    code text,
    description text,
    child_code text,
    parent_code text,
    level text,
    rec_type text,
    bool_data_emissione boolean,
    bool_prezzo_emissione boolean,
    bool_data_scadenza boolean,
    bool_prezzo_rimborso boolean
);


ALTER TABLE genrotit.genrotit_h_tipo_titolo OWNER TO postgres;

--
-- Name: genrotit_movimento; Type: TABLE; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE TABLE genrotit_movimento (
    id character(22) DEFAULT NULL::bpchar NOT NULL,
    __ins_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __del_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __mod_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    gestione_id text,
    data_operazione date,
    titolo_id text,
    quantita numeric(16,8) DEFAULT NULL::numeric,
    prezzo numeric(14,2) DEFAULT NULL::numeric,
    tasso_cambio numeric(16,8) DEFAULT NULL::numeric
);


ALTER TABLE genrotit.genrotit_movimento OWNER TO postgres;

--
-- Name: genrotit_referente; Type: TABLE; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE TABLE genrotit_referente (
    id character(22) DEFAULT NULL::bpchar NOT NULL,
    __ins_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __del_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __mod_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    cognome text,
    nome text,
    mail text,
    telefono text,
    fax text,
    banca_id character(22) DEFAULT NULL::bpchar
);


ALTER TABLE genrotit.genrotit_referente OWNER TO postgres;

--
-- Name: genrotit_tipo_titolo; Type: TABLE; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE TABLE genrotit_tipo_titolo (
    id character(22) DEFAULT NULL::bpchar NOT NULL,
    __ins_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __del_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __mod_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    codice character varying(5) DEFAULT NULL::character varying,
    descrizione character varying(30) DEFAULT NULL::character varying
);


ALTER TABLE genrotit.genrotit_tipo_titolo OWNER TO postgres;

--
-- Name: genrotit_tipo_titolo_campo; Type: TABLE; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE TABLE genrotit_tipo_titolo_campo (
    id character(22) DEFAULT NULL::bpchar NOT NULL,
    __ins_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __del_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __mod_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    tipo_titolo_id character(22) DEFAULT NULL::bpchar,
    campo_id character(22) DEFAULT NULL::bpchar,
    ammesso boolean,
    _row_counter bigint
);


ALTER TABLE genrotit.genrotit_tipo_titolo_campo OWNER TO postgres;

--
-- Name: genrotit_titolo; Type: TABLE; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE TABLE genrotit_titolo (
    id character(22) DEFAULT NULL::bpchar NOT NULL,
    __ins_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __del_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __mod_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    codice text,
    descrizione text,
    h_tipo_titolo_id character(22) DEFAULT NULL::bpchar,
    isin text,
    prezzo_emissione_old text,
    data_emissione date,
    data_scadenza date,
    prezzo_rimborso_old text,
    valuta_codice character varying(3) DEFAULT NULL::character varying,
    area_geografica_id text,
    emittente_id text,
    prezzo_emissione numeric(16,8) DEFAULT NULL::numeric,
    prezzo_rimborso numeric(16,8) DEFAULT NULL::numeric
);


ALTER TABLE genrotit.genrotit_titolo OWNER TO postgres;

--
-- Name: genrotit_userobject; Type: TABLE; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE TABLE genrotit_userobject (
    id character(22) DEFAULT NULL::bpchar NOT NULL,
    __ins_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __del_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __mod_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    code text,
    objtype text,
    pkg text,
    tbl text,
    userid text,
    description text,
    notes text,
    data text,
    authtags text,
    private boolean,
    quicklist boolean,
    flags text
);


ALTER TABLE genrotit.genrotit_userobject OWNER TO postgres;

--
-- Name: genrotit_valuta; Type: TABLE; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE TABLE genrotit_valuta (
    __ins_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __del_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __mod_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    codice character varying(3) DEFAULT NULL::character varying NOT NULL,
    descrizione text
);


ALTER TABLE genrotit.genrotit_valuta OWNER TO postgres;

--
-- Name: genrotit_valuta_storico; Type: TABLE; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE TABLE genrotit_valuta_storico (
    id character(22) DEFAULT NULL::bpchar NOT NULL,
    __ins_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __del_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __mod_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    valuta_codice text,
    data date,
    valore numeric(18,6) DEFAULT NULL::numeric
);


ALTER TABLE genrotit.genrotit_valuta_storico OWNER TO postgres;

--
-- Name: genrotit_valutazione; Type: TABLE; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE TABLE genrotit_valutazione (
    "V" text,
    id character(22) DEFAULT NULL::bpchar NOT NULL,
    __ins_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __del_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    __mod_ts timestamp(6) without time zone DEFAULT NULL::timestamp without time zone,
    data_valutazione date,
    prezzo numeric(14,2) DEFAULT NULL::numeric,
    corso text,
    titolo_id text
);


ALTER TABLE genrotit.genrotit_valutazione OWNER TO postgres;

SET search_path = glbl, pg_catalog;

--
-- Name: glbl_counter; Type: TABLE; Schema: glbl; Owner: postgres; Tablespace: 
--

CREATE TABLE glbl_counter (
    __ins_ts timestamp without time zone,
    __del_ts timestamp without time zone,
    __mod_ts timestamp without time zone,
    codekey character varying(32) NOT NULL,
    code character varying(12),
    pkg character varying(12),
    name text,
    counter bigint,
    last_used date,
    holes text
);


ALTER TABLE glbl.glbl_counter OWNER TO postgres;

--
-- Name: glbl_localita; Type: TABLE; Schema: glbl; Owner: postgres; Tablespace: 
--

CREATE TABLE glbl_localita (
    id character(22) NOT NULL,
    nome character varying(52),
    provincia character(2),
    codice_istat character(6),
    codice_comune character(4),
    prefisso_tel character(4),
    cap character(5)
);


ALTER TABLE glbl.glbl_localita OWNER TO postgres;

--
-- Name: glbl_nazione; Type: TABLE; Schema: glbl; Owner: postgres; Tablespace: 
--

CREATE TABLE glbl_nazione (
    code character(2) NOT NULL,
    name character varying(48),
    code3 character(3),
    nmbr character(3)
);


ALTER TABLE glbl.glbl_nazione OWNER TO postgres;

--
-- Name: glbl_provincia; Type: TABLE; Schema: glbl; Owner: postgres; Tablespace: 
--

CREATE TABLE glbl_provincia (
    sigla character(2) NOT NULL,
    regione character(3),
    nome character varying(30),
    codice_istat character(3),
    ordine bigint,
    ordine_tot character(6),
    cap_valido character(2),
    auxdata text
);


ALTER TABLE glbl.glbl_provincia OWNER TO postgres;

--
-- Name: glbl_regione; Type: TABLE; Schema: glbl; Owner: postgres; Tablespace: 
--

CREATE TABLE glbl_regione (
    sigla character(3) NOT NULL,
    nome character varying(22),
    codice_istat character(2),
    ordine character(6),
    zona character(6)
);


ALTER TABLE glbl.glbl_regione OWNER TO postgres;

--
-- Name: glbl_stradario_cap; Type: TABLE; Schema: glbl; Owner: postgres; Tablespace: 
--

CREATE TABLE glbl_stradario_cap (
    id character(22) NOT NULL,
    cap character varying(8),
    provincia character(2),
    comune character varying(42),
    comune2 character varying(42),
    frazione character varying(42),
    frazione2 character varying(42),
    topo character varying(62),
    topo2 character varying(62),
    pref text,
    n_civico text
);


ALTER TABLE glbl.glbl_stradario_cap OWNER TO postgres;

--
-- Name: glbl_userobject; Type: TABLE; Schema: glbl; Owner: postgres; Tablespace: 
--

CREATE TABLE glbl_userobject (
    id character(22) NOT NULL,
    __ins_ts timestamp without time zone,
    __del_ts timestamp without time zone,
    __mod_ts timestamp without time zone,
    code text,
    objtype text,
    pkg text,
    tbl text,
    userid text,
    description text,
    notes text,
    data text,
    authtags text,
    private boolean,
    quicklist boolean,
    flags text
);


ALTER TABLE glbl.glbl_userobject OWNER TO postgres;

SET search_path = sys, pg_catalog;

--
-- Name: sys_counter; Type: TABLE; Schema: sys; Owner: postgres; Tablespace: 
--

CREATE TABLE sys_counter (
    __ins_ts timestamp without time zone,
    __del_ts timestamp without time zone,
    __mod_ts timestamp without time zone,
    codekey character varying(32) NOT NULL,
    code character varying(12),
    pkg character varying(12),
    name text,
    counter bigint,
    last_used date,
    holes text
);


ALTER TABLE sys.sys_counter OWNER TO postgres;

--
-- Name: sys_external_token; Type: TABLE; Schema: sys; Owner: postgres; Tablespace: 
--

CREATE TABLE sys_external_token (
    id character(22) NOT NULL,
    datetime timestamp without time zone,
    expiry timestamp without time zone,
    allowed_user character varying(32),
    connection_id character(22),
    max_usages integer,
    allowed_host text,
    page_path text,
    method text,
    parameters text,
    exec_user character varying(32)
);


ALTER TABLE sys.sys_external_token OWNER TO postgres;

--
-- Name: sys_external_token_use; Type: TABLE; Schema: sys; Owner: postgres; Tablespace: 
--

CREATE TABLE sys_external_token_use (
    id character(22) NOT NULL,
    external_token_id character(22),
    datetime timestamp without time zone,
    host text
);


ALTER TABLE sys.sys_external_token_use OWNER TO postgres;

--
-- Name: sys_locked_record; Type: TABLE; Schema: sys; Owner: postgres; Tablespace: 
--

CREATE TABLE sys_locked_record (
    id character(22) NOT NULL,
    lock_ts timestamp without time zone,
    lock_table character varying(64),
    lock_pkey character varying(64),
    page_id character(22),
    connection_id character(22),
    username character varying(32)
);


ALTER TABLE sys.sys_locked_record OWNER TO postgres;

--
-- Name: sys_message; Type: TABLE; Schema: sys; Owner: postgres; Tablespace: 
--

CREATE TABLE sys_message (
    id character(22) NOT NULL,
    datetime timestamp without time zone,
    expiry timestamp without time zone,
    dst_page_id character(22),
    dst_user character varying(32),
    dst_connection_id character(22),
    src_page_id character(22),
    src_user character varying(32),
    src_connection_id character(22),
    message_type character varying(12),
    body text
);


ALTER TABLE sys.sys_message OWNER TO postgres;

--
-- Name: sys_userobject; Type: TABLE; Schema: sys; Owner: postgres; Tablespace: 
--

CREATE TABLE sys_userobject (
    id character(22) NOT NULL,
    __ins_ts timestamp without time zone,
    __del_ts timestamp without time zone,
    __mod_ts timestamp without time zone,
    code text,
    objtype text,
    pkg text,
    tbl text,
    userid text,
    description text,
    notes text,
    data text,
    authtags text,
    private boolean,
    quicklist boolean,
    flags text
);


ALTER TABLE sys.sys_userobject OWNER TO postgres;

SET search_path = test15, pg_catalog;

--
-- Name: test15_counter; Type: TABLE; Schema: test15; Owner: postgres; Tablespace: 
--

CREATE TABLE test15_counter (
    __ins_ts timestamp without time zone,
    __del_ts timestamp without time zone,
    __mod_ts timestamp without time zone,
    codekey character varying(32) NOT NULL,
    code character varying(12),
    pkg character varying(12),
    name text,
    counter bigint,
    last_used date,
    holes text
);


ALTER TABLE test15.test15_counter OWNER TO postgres;

--
-- Name: test15_recursive; Type: TABLE; Schema: test15; Owner: postgres; Tablespace: 
--

CREATE TABLE test15_recursive (
    id character(22) NOT NULL,
    __ins_ts timestamp without time zone,
    __del_ts timestamp without time zone,
    __mod_ts timestamp without time zone,
    code text,
    description text,
    parent_id character(22)
);


ALTER TABLE test15.test15_recursive OWNER TO postgres;

--
-- Name: test15_userobject; Type: TABLE; Schema: test15; Owner: postgres; Tablespace: 
--

CREATE TABLE test15_userobject (
    id character(22) NOT NULL,
    __ins_ts timestamp without time zone,
    __del_ts timestamp without time zone,
    __mod_ts timestamp without time zone,
    code text,
    objtype text,
    pkg text,
    tbl text,
    userid text,
    description text,
    notes text,
    data text,
    authtags text,
    private boolean,
    quicklist boolean,
    flags text
);


ALTER TABLE test15.test15_userobject OWNER TO postgres;

SET search_path = adm, pg_catalog;

--
-- Data for Name: adm_audit; Type: TABLE DATA; Schema: adm; Owner: postgres
--

COPY adm_audit (id, __ins_ts, __del_ts, __mod_ts, tablename, event, username, record_pkey, version, data, transaction_id) FROM stdin;
\.


--
-- Data for Name: adm_authorization; Type: TABLE DATA; Schema: adm; Owner: postgres
--

COPY adm_authorization (__ins_ts, __del_ts, __mod_ts, code, user_id, use_ts, used_by, note, remaining_usages, expiry_date) FROM stdin;
\.


--
-- Data for Name: adm_connection; Type: TABLE DATA; Schema: adm; Owner: postgres
--

COPY adm_connection (id, userid, username, ip, start_ts, end_ts, end_reason, user_agent) FROM stdin;
\.


--
-- Data for Name: adm_counter; Type: TABLE DATA; Schema: adm; Owner: postgres
--

COPY adm_counter (__ins_ts, __del_ts, __mod_ts, codekey, code, pkg, name, counter, last_used, holes) FROM stdin;
\.


--
-- Data for Name: adm_datacatalog; Type: TABLE DATA; Schema: adm; Owner: postgres
--

COPY adm_datacatalog (id, __ins_ts, __del_ts, __mod_ts, code, description, child_code, parent_code, level, rec_type, dtype, name_long, name_short, format, options, maxvalue, minvalue, dflt, tip, purpose, ext_ref, related_to, pkg, pkey_field, field_size, tbl, fld, comment, name_full, datacatalog_path, dbkey) FROM stdin;
\.


--
-- Data for Name: adm_doctemplate; Type: TABLE DATA; Schema: adm; Owner: postgres
--

COPY adm_doctemplate (id, __ins_ts, __del_ts, __mod_ts, name, content, templatebag, metadata, varsbag, username, version, locale, maintable, resource_name) FROM stdin;
\.


--
-- Data for Name: adm_htag; Type: TABLE DATA; Schema: adm; Owner: postgres
--

COPY adm_htag (id, __ins_ts, __del_ts, __mod_ts, code, description, child_code, parent_code, level, rec_type, isreserved, note) FROM stdin;
\.


--
-- Data for Name: adm_htmltemplate; Type: TABLE DATA; Schema: adm; Owner: postgres
--

COPY adm_htmltemplate (id, __ins_ts, __del_ts, __mod_ts, name, username, version, data) FROM stdin;
\.


--
-- Data for Name: adm_menu; Type: TABLE DATA; Schema: adm; Owner: postgres
--

COPY adm_menu (id, __ins_ts, __del_ts, __mod_ts, __rec_md5, code, label, basepath, tags, file, description, parameters, "position", _class, _style) FROM stdin;
\.


--
-- Data for Name: adm_permission; Type: TABLE DATA; Schema: adm; Owner: postgres
--

COPY adm_permission (id, __ins_ts, __del_ts, __mod_ts, datacatalog_id, tag_id, view_read, view_add, view_del, form_read, form_add, form_del, form_upd, column_read, column_upd) FROM stdin;
\.


--
-- Data for Name: adm_preference; Type: TABLE DATA; Schema: adm; Owner: postgres
--

COPY adm_preference (__ins_ts, __del_ts, __mod_ts, code, data) FROM stdin;
\.


--
-- Data for Name: adm_record_tag; Type: TABLE DATA; Schema: adm; Owner: postgres
--

COPY adm_record_tag (id, __ins_ts, __del_ts, __mod_ts, tablename, tag, description) FROM stdin;
\.


--
-- Data for Name: adm_served_page; Type: TABLE DATA; Schema: adm; Owner: postgres
--

COPY adm_served_page (page_id, pagename, connection_id, start_ts, end_ts, end_reason) FROM stdin;
\.


--
-- Data for Name: adm_tag; Type: TABLE DATA; Schema: adm; Owner: postgres
--

COPY adm_tag (id, __ins_ts, __del_ts, __mod_ts, __rec_md5, tagname, isreserved, description) FROM stdin;
4l5LUDvaMU2FN40j3Ox8sg	2011-10-27 14:23:07.237009	\N	2011-10-27 14:23:07.237033	\N	_DEV_	\N	\N
MTcLegw3Pgy2JBRFJ5O8Gw	2011-10-27 14:23:07.292848	\N	2011-10-27 14:23:07.292872	\N	admin	\N	\N
L-jtJbDnMMqvPfMDfcvECQ	2011-10-27 14:23:07.297579	\N	2011-10-27 14:23:07.297603	\N	user	\N	\N
\.


--
-- Data for Name: adm_user; Type: TABLE DATA; Schema: adm; Owner: postgres
--

COPY adm_user (id, __ins_ts, __del_ts, __mod_ts, __rec_md5, username, email, firstname, lastname, registration_date, auth_tags, status, md5pwd, locale, preferences, avatar_rootpage) FROM stdin;
\.


--
-- Data for Name: adm_user_tag; Type: TABLE DATA; Schema: adm; Owner: postgres
--

COPY adm_user_tag (id, __ins_ts, __del_ts, __mod_ts, user_id, tag_id) FROM stdin;
\.


--
-- Data for Name: adm_userobject; Type: TABLE DATA; Schema: adm; Owner: postgres
--

COPY adm_userobject (id, __ins_ts, __del_ts, __mod_ts, code, objtype, pkg, tbl, userid, description, notes, data, authtags, private, quicklist, flags) FROM stdin;
\.


SET search_path = genrotit, pg_catalog;

--
-- Data for Name: genrotit_area_geografica; Type: TABLE DATA; Schema: genrotit; Owner: postgres
--

COPY genrotit_area_geografica (id, __ins_ts, __del_ts, __mod_ts, codice, descrizione, valuta_codice) FROM stdin;
\.


--
-- Data for Name: genrotit_banca; Type: TABLE DATA; Schema: genrotit; Owner: postgres
--

COPY genrotit_banca (id, __ins_ts, __del_ts, __mod_ts, codice, descrizione, nome, indirizzo, cap, localita) FROM stdin;
w6RjyxprPJad8ow2_WyIEA	2011-10-11 19:36:58.646481	\N	2011-10-12 12:19:22.362554	BNL	BNL - BNP Paribas	Banca Nazionale del Lavoro	\N	\N	\N
7FlHglLnNPazbDwQNIvRdg	2011-10-11 19:36:14.200217	\N	2011-10-15 17:36:16.694354	BPM	Popolare Milano	Popolare MI	\N	\N	\N
kFa5kvInMLaW0rrJnSz8fw	2011-10-11 19:38:29.885193	\N	2011-10-15 17:36:26.767945	CB	Credito Bergamasco	Credito Bergamasco	\N	\N	\N
Zu9WrwChPUCzL4U_09tiSA	2011-10-11 19:37:17.926443	\N	2011-10-15 17:36:36.949091	IG	Intesa Garanzia	Intesa Garanzia	\N	\N	\N
R7J4_djVMKmtSUw5BOK9_A	2011-10-11 19:37:08.806357	\N	2011-10-15 17:36:52.061634	IP	Intesa Private	Intesa Private	\N	\N	\N
JSaeJOx3MGC2-wHRQaH-AA	2011-10-11 19:37:30.528459	\N	2011-10-15 17:37:23.222694	LLB	LLB	Liechtensteinische Landesbank	\N	\N	\N
urTZiZtJMtWJEGgvvKOgNQ	2011-10-11 19:38:00.568142	\N	2011-10-15 17:37:43.690935	NO	Popolare Novara	Popolare Novara	\N	\N	\N
gEDk34jSO2CHMQG1emAkQQ	2011-10-11 19:38:08.442337	\N	2011-10-15 17:38:20.834783	UBS	UBS	UBS Lugano	\N	\N	\N
zBe_fMJMP1ae26eMIgLp6g	2011-10-11 19:37:39.996428	\N	2011-10-15 17:45:59.662898	BG	Popolare Bergamo	Popolare Bergamo - UBI	\N	\N	\N
HeXrmE1cMrO85edrWKhymg	2011-10-15 17:47:18.084814	\N	2011-10-15 17:48:03.351017	SI	\N	Banco di Sicilia - Unicredit	\N	\N	\N
\.


--
-- Data for Name: genrotit_campo; Type: TABLE DATA; Schema: genrotit; Owner: postgres
--

COPY genrotit_campo (id, __ins_ts, __del_ts, __mod_ts, codice, descrizione, tipo_campo, valori_ammessi, classificazione) FROM stdin;
7c1bIJ7CNU2sUmb8U8sfpA	2011-10-26 11:10:45.08143	\N	2011-10-26 16:33:43.508642	data_emissione	Data di emissione	D	\N	T
8cnM2EnHMtqB5Hea9oUNSQ	2011-10-26 11:10:58.296483	\N	2011-10-26 16:33:50.650587	data_scadenza	Data di scadenza	D	\N	T
ltlyTu88O8q5B9yw6g0T6g	2011-10-26 11:11:13.217453	\N	2011-10-26 16:33:56.916234	indic	Indicizzazione	B	\N	T
7J4OrjPsPiGDAGqc-KFU8Q	2011-10-31 18:18:34.868242	\N	2011-10-31 18:18:34.868317	esiste_cedola	Cedola	B	\N	T
DmwGJ_JNOD2_MiMbRSkXAA	2011-10-31 18:19:17.245839	\N	2011-10-31 18:19:17.245901	period_cedola	Periodicità cedola	T	Trimestrale, Semestrale, Annuale	T
wx59NgxWN-mWVG91mx4aKQ	2011-10-31 18:20:04.791896	\N	2011-10-31 18:20:04.791957	valuta	Valuta	T	da tabella valute!	T
56K4BDe6OW6liPgsh-_lyA	2011-10-31 18:20:22.893668	\N	2011-10-31 18:20:22.893729	isin	ISIN	T	\N	T
GPbZX9FiNsS5-0Ye94mBxg	2011-10-31 18:21:04.929457	\N	2011-10-31 18:21:04.929522	data_op	Data operazione	D	\N	M
FkE7N8AxNwm1PyZgpXZByA	2011-10-31 18:21:29.589047	\N	2011-10-31 18:21:29.589108	quant	Quantità	N	\N	M
gy2-UhOONnayUglYYyxddg	2011-10-31 18:21:45.882032	\N	2011-10-31 18:21:45.882092	nominali	Nominali	L	\N	M
Axc0pxiJP-CDYrzoVm4ieQ	2011-10-31 18:22:20.408811	\N	2011-10-31 18:22:20.408871	cambio	Tasso di cambio	N	\N	M
slFFyP7LPByfxNtvNSh7DA	2011-10-31 18:22:33.705442	\N	2011-10-31 18:22:33.705503	indic	Indicizzazione	N	\N	M
3C6vHeMSNPOgTG1QN_7XLw	2011-10-31 18:23:05.238787	\N	2011-10-31 18:23:05.238848	rateo	Rateo di cedola	N	\N	M
8G1OhR8yMpC6rd8j5WBe0w	2011-10-31 18:23:30.062712	\N	2011-10-31 18:23:30.062772	comm	Commissioni applicate	N	\N	M
kx9vbJo2PTeCqUISQL-8YA	2011-10-31 18:22:01.529337	\N	2011-10-31 18:24:18.163786	prezzo	Prezzo	N	\N	M
6SFMtZQhOJ-0wHjDYLDljQ	2011-10-31 18:25:58.655209	\N	2011-10-31 18:25:58.655271	corso	Corso	N	\N	M
zD2sN4C_MOOyGN2qKZPhaQ	2011-10-31 18:27:08.053771	\N	2011-10-31 18:27:08.053832	corso	Corso di valutazione	N	\N	V
X7b_PNzfM5yMDHmy7S0YtA	2011-10-31 18:27:21.731669	\N	2011-10-31 18:27:21.73173	prezzo	Prezzo di valutazione	N	\N	V
R9wBJCKzPXqUr7Ef71zMbg	2011-10-31 18:27:34.711821	\N	2011-10-31 18:27:34.711881	cambio	Cambio di valutazione	N	\N	V
Ob5Uuy0VOJuGzb32wgIzfA	2011-10-26 11:12:00.272938	\N	2011-11-21 10:11:07.295416	corso_emissione	Corso di emissione	P	\N	T
n1GRkI2fPyGNKB0KnSG_EQ	2011-10-26 11:12:37.334263	\N	2011-11-21 10:11:24.311447	corso_rimborso	Corso di rimborso	P	\N	T
2ZE7TG2tORWeipOeVLrR8Q	2011-11-21 10:14:52.54949	\N	2011-11-21 10:14:52.54955	distr_proventi	Distribuzione di proventi	B	\N	T
\.


--
-- Data for Name: genrotit_counter; Type: TABLE DATA; Schema: genrotit; Owner: postgres
--

COPY genrotit_counter (__ins_ts, __del_ts, __mod_ts, codekey, code, pkg, name, counter, last_used, holes) FROM stdin;
\.


--
-- Data for Name: genrotit_emittente; Type: TABLE DATA; Schema: genrotit; Owner: postgres
--

COPY genrotit_emittente (id, __ins_ts, __del_ts, __mod_ts, codice, descrizione, area_geografica_id) FROM stdin;
XE9RXiQPPgisVB4RjsE6Sw	2011-10-20 10:39:19.687737	\N	2011-10-20 10:39:19.687799		Italia	\N
\.


--
-- Data for Name: genrotit_gestione; Type: TABLE DATA; Schema: genrotit; Owner: postgres
--

COPY genrotit_gestione (id, __ins_ts, __del_ts, __mod_ts, banca_id, codice, descrizione, conto, valuta_codice) FROM stdin;
9fMk9jcFNfeGti-eUr8_zw	2011-10-24 15:24:37.089914	\N	2011-10-24 15:24:37.089974	7FlHglLnNPazbDwQNIvRdg	\N	\N	BP6368	EUR
PxJtCudLMeG5q3zLNE9fZA	2011-10-24 15:27:47.256588	\N	2011-10-24 15:27:47.256684	w6RjyxprPJad8ow2_WyIEA	\N	\N	BN8011	EUR
rM2rejDkOkSv8XmJHz0-Cw	2011-10-24 15:28:07.945132	\N	2011-10-24 15:28:07.945192	kFa5kvInMLaW0rrJnSz8fw	\N	\N	CB3485	EUR
DG3ApEinOzuV1hS6vmr_qw	2011-10-24 15:28:31.92834	\N	2011-10-24 15:28:31.928419	Zu9WrwChPUCzL4U_09tiSA	\N	\N	IP7037	EUR
ohz3wGbsMFadqETFUhdajg	2011-10-24 15:29:03.768688	\N	2011-10-24 15:29:03.768748	R7J4_djVMKmtSUw5BOK9_A	\N	\N	IP7037	EUR
sOFBx4TFOymEFQjY3SGf-w	2011-10-24 15:29:24.418164	\N	2011-10-24 15:29:33.914802	JSaeJOx3MGC2-wHRQaH-AA	\N	\N	LLB151	EUR
_aMpQFxcOpaI6LjteIGFEA	2011-10-24 15:29:54.437051	\N	2011-10-24 15:29:54.437143	zBe_fMJMP1ae26eMIgLp6g	\N	\N	PB4005	EUR
TqCAH_jmONWF9CsicDxdXw	2011-10-24 15:30:11.914047	\N	2011-10-24 15:30:11.914106	urTZiZtJMtWJEGgvvKOgNQ	\N	\N	PN2007	EUR
otNQ9lwuNwmJYVke3O_7Tw	2011-10-24 15:31:42.409469	\N	2011-10-24 15:31:42.40953	HeXrmE1cMrO85edrWKhymg	\N	\N	SI4547	EUR
eLsz9ayvOrW-qjdCdIG6HA	2011-10-24 15:32:24.918224	\N	2011-10-24 15:32:24.918284	gEDk34jSO2CHMQG1emAkQQ	\N	\N	UB1460 (EUR)	EUR
ECLBN22xOIWMs0j3l5_4Xg	2011-10-24 15:32:03.474093	\N	2011-10-24 15:32:36.964533	gEDk34jSO2CHMQG1emAkQQ	\N	\N	UB1401 (CHF)	EUR
\.


--
-- Data for Name: genrotit_h_tipo_titolo; Type: TABLE DATA; Schema: genrotit; Owner: postgres
--

COPY genrotit_h_tipo_titolo (id, __ins_ts, __del_ts, __mod_ts, code, description, child_code, parent_code, level, rec_type, bool_data_emissione, bool_prezzo_emissione, bool_data_scadenza, bool_prezzo_rimborso) FROM stdin;
MvLh9YUKN82UHiAXt3nJKQ	2011-10-15 17:53:06.123582	\N	2011-10-20 16:56:22.601717	AZ	Azioni	AZ	\N	0	\N	f	f	f	f
4w1Izg94OQmTj3xUOTWK4g	2011-10-15 17:52:44.06969	\N	2011-10-20 16:57:00.945277	BC	BOT e CTZ	BC	\N	0	\N	t	t	t	t
dGcVW7y-NlCrWbTAGGUpFQ	2011-10-15 17:52:53.589882	\N	2011-10-20 16:57:17.114567	FO	Fondi comuni	FO	\N	0	\N	f	f	f	f
Cxf15p35MteURB62fkY6EQ	2011-10-15 17:52:34.019024	\N	2011-10-20 16:57:23.046858	OB	Obbligazioni	OB	\N	0	\N	t	t	t	t
\.


--
-- Data for Name: genrotit_movimento; Type: TABLE DATA; Schema: genrotit; Owner: postgres
--

COPY genrotit_movimento (id, __ins_ts, __del_ts, __mod_ts, gestione_id, data_operazione, titolo_id, quantita, prezzo, tasso_cambio) FROM stdin;
\.


--
-- Data for Name: genrotit_referente; Type: TABLE DATA; Schema: genrotit; Owner: postgres
--

COPY genrotit_referente (id, __ins_ts, __del_ts, __mod_ts, cognome, nome, mail, telefono, fax, banca_id) FROM stdin;
b6-_dhj8OhiZtWBuGpuMQg	2011-10-31 18:15:14.861871	\N	2011-10-31 18:15:14.861932	Giuseppe	Verderio	\N	\N	\N	R7J4_djVMKmtSUw5BOK9_A
\.


--
-- Data for Name: genrotit_tipo_titolo; Type: TABLE DATA; Schema: genrotit; Owner: postgres
--

COPY genrotit_tipo_titolo (id, __ins_ts, __del_ts, __mod_ts, codice, descrizione) FROM stdin;
JvGSAwAlMxixsiFQ17GhAA	2011-10-11 19:46:48.41254	\N	2011-10-11 19:46:48.412599	bc	BOT e CTZ
ZJcbvDcAMZa1U28AqbyMGg	2011-10-11 19:47:07.35308	\N	2011-10-11 19:47:07.353168	az	Azioni
N-B6PRKyO2SnaA71J8-Gzg	2011-10-11 19:46:56.989843	\N	2011-10-11 19:48:46.032067	fo	Fondi comuni
1DVjT9eTPGWIoFPKimWcLg	2011-10-11 19:46:15.680748	\N	2011-10-11 19:48:54.259347	ob	Obbligazioni
\.


--
-- Data for Name: genrotit_tipo_titolo_campo; Type: TABLE DATA; Schema: genrotit; Owner: postgres
--

COPY genrotit_tipo_titolo_campo (id, __ins_ts, __del_ts, __mod_ts, tipo_titolo_id, campo_id, ammesso, _row_counter) FROM stdin;
rAv1jDViN4uatJzdzUE0UQ	2011-10-26 11:15:31.333446	\N	2011-10-26 11:15:31.333474	Cxf15p35MteURB62fkY6EQ	7c1bIJ7CNU2sUmb8U8sfpA	\N	\N
dTWpdSznPUOuuwIlXNXd7A	2011-10-26 11:15:31.368603	\N	2011-10-26 11:15:31.368628	Cxf15p35MteURB62fkY6EQ	8cnM2EnHMtqB5Hea9oUNSQ	\N	\N
mGUsTgYZM1mP6vYjLK_NnQ	2011-10-26 11:15:31.369665	\N	2011-10-26 11:15:31.369683	Cxf15p35MteURB62fkY6EQ	Ob5Uuy0VOJuGzb32wgIzfA	\N	\N
CwX1AZ7nN26QBkvQ1-8MQQ	2011-10-26 11:15:31.370626	\N	2011-10-26 11:15:31.370644	Cxf15p35MteURB62fkY6EQ	n1GRkI2fPyGNKB0KnSG_EQ	\N	\N
twcUhgAqNMe1HQThFmIM-g	2011-11-21 10:08:35.737406	\N	2011-11-21 10:08:35.737424	MvLh9YUKN82UHiAXt3nJKQ	56K4BDe6OW6liPgsh-_lyA	\N	\N
f8ZwMy0fNyqGbDzgErIc8A	2011-11-21 10:08:56.870972	\N	2011-11-21 10:08:56.87099	MvLh9YUKN82UHiAXt3nJKQ	GPbZX9FiNsS5-0Ye94mBxg	\N	\N
SrfIKmk-NIudO3V0H7Kpjw	2011-11-21 10:08:58.867505	\N	2011-11-21 10:08:58.867526	MvLh9YUKN82UHiAXt3nJKQ	FkE7N8AxNwm1PyZgpXZByA	\N	\N
hAFNmhnnNXWAO60MyZ1UrA	2011-11-21 10:09:31.220999	\N	2011-11-21 10:09:31.221016	MvLh9YUKN82UHiAXt3nJKQ	6SFMtZQhOJ-0wHjDYLDljQ	\N	\N
h9mBVn8WMfmxyklaTxJBkQ	2011-11-21 10:09:33.879733	\N	2011-11-21 10:09:33.879751	MvLh9YUKN82UHiAXt3nJKQ	8G1OhR8yMpC6rd8j5WBe0w	\N	\N
gK-cIZ9_NDyYvaSPRxT18g	2011-11-21 10:09:45.7123	\N	2011-11-21 10:09:45.712318	MvLh9YUKN82UHiAXt3nJKQ	zD2sN4C_MOOyGN2qKZPhaQ	\N	\N
rNNUHpvhO96BStY0ZjH44w	2011-11-21 10:11:48.687686	\N	2011-11-21 10:11:48.687708	4w1Izg94OQmTj3xUOTWK4g	7c1bIJ7CNU2sUmb8U8sfpA	\N	\N
1LyxPjveNoaPO26WrHisbQ	2011-11-21 10:11:51.22396	\N	2011-11-21 10:11:51.22399	4w1Izg94OQmTj3xUOTWK4g	Ob5Uuy0VOJuGzb32wgIzfA	\N	\N
e3U2C3v1P_C8-XoyxQ7Mqw	2011-11-21 10:11:53.366283	\N	2011-11-21 10:11:53.366316	4w1Izg94OQmTj3xUOTWK4g	8cnM2EnHMtqB5Hea9oUNSQ	\N	\N
CMkJe0-KMga7mnDheTcL-Q	2011-11-21 10:11:55.835839	\N	2011-11-21 10:11:55.835858	4w1Izg94OQmTj3xUOTWK4g	n1GRkI2fPyGNKB0KnSG_EQ	\N	\N
Fm_12F0oNKqTfZLRk3angQ	2011-11-21 10:12:05.918594	\N	2011-11-21 10:12:05.918613	4w1Izg94OQmTj3xUOTWK4g	56K4BDe6OW6liPgsh-_lyA	\N	\N
ipAxu8WAPSinH8cp1IpP_Q	2011-11-21 10:12:33.534085	\N	2011-11-21 10:12:33.534103	4w1Izg94OQmTj3xUOTWK4g	ltlyTu88O8q5B9yw6g0T6g	\N	\N
D_R8_qkeO1OOmvFL4Nqg6A	2011-11-21 10:12:38.27752	\N	2011-11-21 10:12:38.277538	4w1Izg94OQmTj3xUOTWK4g	7J4OrjPsPiGDAGqc-KFU8Q	\N	\N
9HmCDftsPE-2Dk-fz3d0cA	2011-11-21 10:12:49.37362	\N	2011-11-21 10:12:49.373641	4w1Izg94OQmTj3xUOTWK4g	GPbZX9FiNsS5-0Ye94mBxg	\N	\N
k_nugUjoPGGSX6VwXRc7Zw	2011-11-21 10:12:52.060646	\N	2011-11-21 10:12:52.060664	4w1Izg94OQmTj3xUOTWK4g	gy2-UhOONnayUglYYyxddg	\N	\N
Dt29D88VOq6KTMbJ74L6iA	2011-11-21 10:12:57.476587	\N	2011-11-21 10:12:57.476609	4w1Izg94OQmTj3xUOTWK4g	6SFMtZQhOJ-0wHjDYLDljQ	\N	\N
Rn1sBsO9N9C-_3uTysTpmg	2011-11-21 10:13:19.947696	\N	2011-11-21 10:13:19.947714	4w1Izg94OQmTj3xUOTWK4g	8G1OhR8yMpC6rd8j5WBe0w	\N	\N
YMg-pFnfPwe28RuqG-dApw	2011-11-21 10:13:28.832947	\N	2011-11-21 10:13:28.832969	4w1Izg94OQmTj3xUOTWK4g	zD2sN4C_MOOyGN2qKZPhaQ	\N	\N
_IhPqO6aOpmv4GL0BEnv2w	2011-11-21 10:13:47.266362	\N	2011-11-21 10:13:47.26638	dGcVW7y-NlCrWbTAGGUpFQ	56K4BDe6OW6liPgsh-_lyA	\N	\N
OTZP92YEMT2S3shdDiiZPQ	2011-11-21 10:15:12.71234	\N	2011-11-21 10:15:12.712359	dGcVW7y-NlCrWbTAGGUpFQ	wx59NgxWN-mWVG91mx4aKQ	\N	\N
N7XHzv4TPoGZSVahip7cuw	2011-11-21 10:15:21.299099	\N	2011-11-21 10:15:21.299119	dGcVW7y-NlCrWbTAGGUpFQ	GPbZX9FiNsS5-0Ye94mBxg	\N	\N
VNg8jAUoN3-vU7RGnyvbvQ	2011-11-21 10:15:23.438785	\N	2011-11-21 10:15:23.438803	dGcVW7y-NlCrWbTAGGUpFQ	FkE7N8AxNwm1PyZgpXZByA	\N	\N
_dWy174NP_iTRzEWo5xaIg	2011-11-21 10:15:26.772188	\N	2011-11-21 10:15:26.772206	dGcVW7y-NlCrWbTAGGUpFQ	kx9vbJo2PTeCqUISQL-8YA	\N	\N
deAOSg2zOtqtiTl9qB_RJw	2011-11-21 10:15:31.795191	\N	2011-11-21 10:15:31.795209	dGcVW7y-NlCrWbTAGGUpFQ	Axc0pxiJP-CDYrzoVm4ieQ	\N	\N
OvBugprEOdK3pdPmVf8_Lg	2011-11-21 10:15:33.879603	\N	2011-11-21 10:15:33.879621	dGcVW7y-NlCrWbTAGGUpFQ	8G1OhR8yMpC6rd8j5WBe0w	\N	\N
W85b3DTeM2Oi78yubIxNfQ	2011-11-21 10:15:39.933192	\N	2011-11-21 10:15:39.933211	dGcVW7y-NlCrWbTAGGUpFQ	X7b_PNzfM5yMDHmy7S0YtA	\N	\N
X5g0Nq0XP26ZatL3Ww82kg	2011-11-21 10:15:41.899569	\N	2011-11-21 10:15:41.899587	dGcVW7y-NlCrWbTAGGUpFQ	R9wBJCKzPXqUr7Ef71zMbg	\N	\N
Sc83VKD8OHO543fFc5zyaQ	2011-11-21 10:16:57.696975	\N	2011-11-21 10:16:57.696993	Cxf15p35MteURB62fkY6EQ	ltlyTu88O8q5B9yw6g0T6g	\N	\N
1FdtDaKYNGmV9h70K4_YOA	2011-11-21 10:16:59.708203	\N	2011-11-21 10:16:59.708221	Cxf15p35MteURB62fkY6EQ	7J4OrjPsPiGDAGqc-KFU8Q	\N	\N
PApeKxfCMimTyWaEQwE6ug	2011-11-21 10:17:03.735818	\N	2011-11-21 10:17:03.735842	Cxf15p35MteURB62fkY6EQ	DmwGJ_JNOD2_MiMbRSkXAA	\N	\N
LiWrylyXOb2R7aU0FqbmXw	2011-11-21 10:17:05.476774	\N	2011-11-21 10:17:05.476792	Cxf15p35MteURB62fkY6EQ	wx59NgxWN-mWVG91mx4aKQ	\N	\N
fDIB8ynvMf-D05Ze-KmxSA	2011-11-21 10:17:07.471359	\N	2011-11-21 10:17:07.471377	Cxf15p35MteURB62fkY6EQ	56K4BDe6OW6liPgsh-_lyA	\N	\N
G7Qyez9CO0qG0CBcpAxYGA	2011-11-21 10:17:15.953267	\N	2011-11-21 10:17:15.953284	Cxf15p35MteURB62fkY6EQ	GPbZX9FiNsS5-0Ye94mBxg	\N	\N
SJQoB2F1PVyT5qcsQi05oQ	2011-11-21 10:17:17.930263	\N	2011-11-21 10:17:17.930288	Cxf15p35MteURB62fkY6EQ	gy2-UhOONnayUglYYyxddg	\N	\N
8PyRcaGKPzqPSmq8sCl_IA	2011-11-21 10:17:19.970564	\N	2011-11-21 10:17:19.970582	Cxf15p35MteURB62fkY6EQ	6SFMtZQhOJ-0wHjDYLDljQ	\N	\N
lA5RT1EFPSmvgIjbzi3SlQ	2011-11-21 10:17:31.121244	\N	2011-11-21 10:17:31.121262	Cxf15p35MteURB62fkY6EQ	Axc0pxiJP-CDYrzoVm4ieQ	\N	\N
EC1EHmNGM3SUVJEDoQMzpg	2011-11-21 10:17:32.656822	\N	2011-11-21 10:17:32.656844	Cxf15p35MteURB62fkY6EQ	slFFyP7LPByfxNtvNSh7DA	\N	\N
9gWKGrnKNqeorsMf8MIzYQ	2011-11-21 10:17:44.291123	\N	2011-11-21 10:17:44.291149	Cxf15p35MteURB62fkY6EQ	3C6vHeMSNPOgTG1QN_7XLw	\N	\N
wckLPk28NDmZXlGIBJ0lKw	2011-11-21 10:17:45.897371	\N	2011-11-21 10:17:45.897389	Cxf15p35MteURB62fkY6EQ	8G1OhR8yMpC6rd8j5WBe0w	\N	\N
IQgeZp1yN8yYsW0ovvttNA	2011-11-21 10:17:52.840881	\N	2011-11-21 10:17:52.840899	Cxf15p35MteURB62fkY6EQ	zD2sN4C_MOOyGN2qKZPhaQ	\N	\N
wbXm7qoGM4W6-Kaua961KA	2011-11-21 10:17:55.166851	\N	2011-11-21 10:17:55.166869	Cxf15p35MteURB62fkY6EQ	R9wBJCKzPXqUr7Ef71zMbg	\N	\N
\.


--
-- Data for Name: genrotit_titolo; Type: TABLE DATA; Schema: genrotit; Owner: postgres
--

COPY genrotit_titolo (id, __ins_ts, __del_ts, __mod_ts, codice, descrizione, h_tipo_titolo_id, isin, prezzo_emissione_old, data_emissione, data_scadenza, prezzo_rimborso_old, valuta_codice, area_geografica_id, emittente_id, prezzo_emissione, prezzo_rimborso) FROM stdin;
rvgI70ZIMfawjgyKqTHwLg	2011-10-15 19:08:53.927615	\N	2011-10-18 19:24:38.86501	\N	FRANK EMERG MKT BOND USD	dGcVW7y-NlCrWbTAGGUpFQ	LU0195951966	\N	\N	\N	\N	USD	\N	\N	\N	\N
Kc3aM9BWN4GWJG6uMRF3PA	2011-10-15 19:11:27.471322	\N	2011-10-19 09:52:13.131344	\N	INVESCO EM MKTSBOND	dGcVW7y-NlCrWbTAGGUpFQ	IE00B01VQG96	\N	\N	\N	\N	EUR	\N	\N	\N	\N
KcZh2hfyNAC3frcuXiTltA	2011-10-15 19:12:37.54925	\N	2011-10-19 09:52:21.50704	\N	SCHRODER ISD E CORP	dGcVW7y-NlCrWbTAGGUpFQ	LU0113258742	\N	\N	\N	\N	EUR	\N	\N	\N	\N
e0L-aIUIN4CQTa-e2wBUgw	2011-10-15 19:11:54.748462	\N	2011-10-19 09:56:00.587628	\N	JB LOCAL EM.BOND$LUX	dGcVW7y-NlCrWbTAGGUpFQ	LU0107852435	\N	\N	\N	\N	EUR	\N	\N	\N	\N
-Vg8wvkINWuMUPwpbtPk_Q	2011-10-15 19:01:21.725296	\N	2011-10-21 14:38:03.41125	\N	BUNDESREP 2,25% 2015	Cxf15p35MteURB62fkY6EQ	DE0001141570	100.280	2010-04-10	2015-04-10	100	EUR	\N	\N	100.28000000	100.00000000
HixBfAetN9yPPXrKNpKfsQ	2011-10-15 18:32:46.897135	\N	2011-10-21 14:42:16.746359	\N	DEXIA CREDIOP 06/11	Cxf15p35MteURB62fkY6EQ	IT0004119670	100	2006-10-30	2011-10-30	100	EUR	\N	\N	100.00000000	100.00000000
JA3zvWEPNEGvXQNmnrjl7w	2011-10-18 19:34:46.961312	\N	2011-10-21 14:42:34.316756	\N	ISP 2010/2015 3,10%	Cxf15p35MteURB62fkY6EQ	IT0004583420	100.00	2010-09-22	2015-09-22	100.00	EUR	\N	\N	100.00000000	100.00000000
LmyAZjPaN2yyl0J9zCVWsA	2011-10-15 18:26:01.947191	\N	2011-10-21 14:42:53.215692	\N	CENTROBCA 06/11 TV%	Cxf15p35MteURB62fkY6EQ	IT0004011166	100	2006-03-15	2011-03-15	100	EUR	\N	\N	100.00000000	100.00000000
RBqowGxNNGGnoV-fxQI6NQ	2011-10-15 18:31:59.401367	\N	2011-10-21 14:43:39.304116	\N	DEXIA CR.10/16 TV%	Cxf15p35MteURB62fkY6EQ	IT0004607286	100	2010-05-31	2016-05-31	100	EUR	\N	\N	100.00000000	100.00000000
-lxU8ezWN1q2HHFSyfEMTA	2011-10-15 18:34:46.653836	\N	2011-10-21 14:39:23.525434	\N	Mediobanca 14 TM  EU	Cxf15p35MteURB62fkY6EQ	XS0414961002	100	2009-04-30	2014-04-30	100	EUR	\N	\N	100.00000000	100.00000000
2j_GtXIhNgGyjunW3hGyNw	2011-10-15 18:04:09.837599	\N	2011-10-21 14:39:53.647888	\N	ABN 12 Luxory BKT-EU	Cxf15p35MteURB62fkY6EQ	IT0006628595	100	2007-03-26	2012-03-26	100	EUR	\N	\N	100.00000000	100.00000000
5fIKqSVPPlyWXSAZuxXRsw	2011-10-15 18:07:30.120856	\N	2011-10-21 14:40:04.994398	\N	BCA IMI 14 TV 29.5EU	Cxf15p35MteURB62fkY6EQ	XS0415046845	100	2009-05-29	2014-05-29	100	EUR	\N	\N	100.00000000	100.00000000
75Esk0UNNLKG02Tt_Q6slg	2011-10-15 18:12:16.104973	\N	2011-10-21 14:40:12.985673	\N	BPM 08/18 TV 20/10 S	Cxf15p35MteURB62fkY6EQ	IT0004396492	100	2008-10-20	2018-10-20	100	EUR	\N	\N	100.00000000	100.00000000
85dyCWkDOLiLn0y1DfhqeA	2011-10-18 19:30:00.121101	\N	2011-10-21 14:40:42.376965	\N	CCTEU DC15 TV	Cxf15p35MteURB62fkY6EQ	IT0004620305	99.883	2010-06-15	2015-12-15	100	EUR	\N	\N	99.88000000	100.00000000
89bzdd_uMlOZ12h5jsGyYQ	2011-10-15 19:07:58.85011	\N	2011-10-21 14:41:02.5988	\N	FRANCE OAT 1% 17	Cxf15p35MteURB62fkY6EQ	FR0010235176	98.550	2002-07-25	2017-07-25	100	EUR	\N	\N	98.55000000	100.00000000
AoxcfpnFN7mqJ0qESbIzgg	2011-10-15 19:12:24.388307	\N	2011-10-21 14:41:27.833148	\N	MEDIOBANCA FRN 2016	Cxf15p35MteURB62fkY6EQ	XS0270008864	99.862	2006-10-11	2016-10-11	100	EUR	\N	\N	99.86000000	100.00000000
Bx-TEUouOA2JBsXcXHDlBA	2011-10-15 19:04:27.383306	\N	2011-10-21 14:41:42.205443	\N	CTZ-29FB12 24M	4w1Izg94OQmTj3xUOTWK4g	IT0004572910	96.820	2010-03-01	2012-02-29	100	EUR	\N	\N	96.82000000	100.00000000
COMntAp0OhmcIK0t6NdfLg	2011-10-15 19:13:41.778358	\N	2011-10-21 14:41:52.247052	\N	WPP PLC 4,375% 13	Cxf15p35MteURB62fkY6EQ	XS0275759602	99.705	2006-12-05	2013-12-05	100	EUR	\N	\N	99.71000000	100.00000000
HDpt867IO3q_clCcCKKh5w	2011-10-15 18:06:52.151615	\N	2011-10-21 14:41:59.785966	\N	ABN AMRO BK	Cxf15p35MteURB62fkY6EQ	NL0006182867	100	2008-02-27	2013-02-27	100	EUR	\N	\N	100.00000000	100.00000000
M17pxd6AM2OP4s3yBCWdGQ	2011-10-18 19:31:51.807216	\N	2011-10-21 14:43:11.268127	\N	INTESA SANPAOLO 08/13 TM	Cxf15p35MteURB62fkY6EQ	IT0004352594	100.00	2008-04-30	2013-04-30	100.00	EUR	\N	\N	100.00000000	100.00000000
mkLVc-cXMJC6-8rifLCJ8w	2011-10-15 19:05:52.355687	\N	2011-10-19 10:00:41.82586	\N	DWS INVEST CONVERTIB	dGcVW7y-NlCrWbTAGGUpFQ	LU0179220412	\N	\N	\N	\N	EUR	\N	\N	\N	\N
MumHxPU8Mfe4-6laZuWg-w	2011-10-15 19:02:46.411734	\N	2011-10-21 15:16:08.858095	\N	CCTE-OT17 TV EUR	Cxf15p35MteURB62fkY6EQ	IT0004652175	99.789	2010-10-15	2017-10-15	100	EUR	\N	\N	99.78900000	100.00000000
TdjpBWz4PRG4FO89eZDd0w	2011-10-15 18:01:27.663956	\N	2011-10-21 15:16:39.839931	\N	BTP 4% 07-15/4/2012	Cxf15p35MteURB62fkY6EQ	IT0004220627	99.4	2007-04-15	2012-04-15	100	EUR	\N	\N	99.40000000	100.00000000
TgP2Qvf6PNyWwsOdwifcfg	2011-10-15 18:38:09.786435	\N	2011-10-21 15:16:49.606939	\N	UBS 17 3,35%	Cxf15p35MteURB62fkY6EQ	XS0490865986	100	2010-03-31	2017-03-31	100	EUR	\N	\N	100.00000000	100.00000000
TnnWfZNaMOmIWWPSN-sKNg	2011-10-15 18:34:17.824873	\N	2011-10-21 15:17:30.244553	\N	Mediobanca 13 RECYC-EU	Cxf15p35MteURB62fkY6EQ	XS0348927509	100	2008-03-31	2013-03-31	100	EUR	\N	\N	100.00000000	100.00000000
WvUcPQoqNMa6CLseJYneLQ	2011-10-15 19:05:23.842847	\N	2011-10-21 15:17:45.196845	\N	CTZ-31MZ11 24M	4w1Izg94OQmTj3xUOTWK4g	IT0004480858	95.960	2009-04-01	2011-03-31	100	EUR	\N	\N	95.96000000	100.00000000
XCPEC5ojPuuPdTkCHDPtyA	2011-10-15 18:59:34.340657	\N	2011-10-21 15:18:01.187618	\N	BTP-15ST17 2,10% IND	Cxf15p35MteURB62fkY6EQ	IT0004085210	99.527	2006-03-15	2017-09-15	100	EUR	\N	\N	99.52700000	100.00000000
XcQYI_BeOmu4z7s_rX7WSw	2011-10-15 18:30:24.573509	\N	2011-10-21 15:18:13.381035	\N	DEXIA CR 10/15 TV%	Cxf15p35MteURB62fkY6EQ	IT0004558919	100	2010-01-29	2015-01-29	100	EUR	\N	\N	100.00000000	100.00000000
Y2Md2Vf5PECcM4t0Mec2Mg	2011-10-15 18:57:40.549762	\N	2011-10-21 15:18:39.641918	\N	BTP-15ST 2011 3,75%	Cxf15p35MteURB62fkY6EQ	IT0004112816	100.170	2006-09-15	2011-09-15	100	EUR	\N	\N	100.17000000	100.00000000
YjgG5sjqOGe-9-RSgUsdgA	2011-10-15 18:26:48.513525	\N	2011-10-21 15:18:48.203034	\N	DBK 15 TV% Inflat EU	Cxf15p35MteURB62fkY6EQ	XS0498844785	100	2010-04-30	2015-04-30	100	EUR	\N	\N	100.00000000	100.00000000
ZvauIFbaOj64THZnA8DKlw	2011-10-15 17:59:14.79681	\N	2011-10-21 15:18:55.421205	\N	BTP 3,75% 06-15-9-11	Cxf15p35MteURB62fkY6EQ	IT0004112816	100	2006-09-15	2011-09-15	100	EUR	\N	\N	100.00000000	100.00000000
_SPuse3ENbSwDOvhJNcQIA	2011-10-15 19:11:09.806049	\N	2011-10-21 15:19:09.499538	\N	GE CAP EUR FRN 07/14	Cxf15p35MteURB62fkY6EQ	XS0197508764	99.640	2004-07-28	2014-07-28	100	EUR	\N	\N	99.64000000	100.00000000
aDOkGjONP8u1pXsV-7msoQ	2011-10-15 18:56:47.843071	\N	2011-10-21 15:19:18.716498	\N	BTP-15AP 2012 4,00%	Cxf15p35MteURB62fkY6EQ	IT0004220627	99.400	2007-04-15	2012-04-15	100	EUR	\N	\N	99.40000000	100.00000000
d6_SkV66MmaBc9EBtNKkrQ	2011-10-15 18:50:09.469778	\N	2011-10-21 15:19:32.532588	\N	BOT-15LG11 ANN	4w1Izg94OQmTj3xUOTWK4g	IT0004622343	98.601	2010-07-15	2011-07-15	100	EUR	\N	\N	98.60100000	100.00000000
eYLXmeHzNCKUXQEGElcISQ	2011-10-15 18:36:31.225717	\N	2011-10-21 15:21:26.037895	\N	Merrill 12 TV 9.2 EU	Cxf15p35MteURB62fkY6EQ	XS0279415169	100	2007-02-09	2012-02-09	100	EUR	\N	\N	100.00000000	100.00000000
h1zTZfXCMxWl38axym5mDQ	2011-10-18 19:32:39.759911	\N	2011-10-21 15:21:40.748653	\N	INTESA SANPAOLO 09/12 TM	Cxf15p35MteURB62fkY6EQ	IT0004482995	100.00	2009-04-30	2012-04-30	100.00	EUR	\N	\N	100.00000000	100.00000000
jVbkBJEhPJiCk2dKb6hN0w	2011-10-15 18:35:18.902217	\N	2011-10-21 15:21:50.959816	\N	MERRIL 12 BRIC40-EU	Cxf15p35MteURB62fkY6EQ	XS0287035462	100	2007-03-21	2012-03-21	100	EUR	\N	\N	100.00000000	100.00000000
jjFiz_Z9NJO1EALUrSfOrQ	2011-10-15 18:55:59.180024	\N	2011-10-21 15:22:01.168331	\N	BTP-01ST 2019 4,25%	Cxf15p35MteURB62fkY6EQ	IT0004489610	99.200	2009-03-01	2019-11-01	100	EUR	\N	\N	99.20000000	100.00000000
kImM3KAOPval_O4RFEwklA	2011-10-15 19:09:37.247974	\N	2011-10-21 15:22:13.131092	\N	GE CAP 4,125% 2016	Cxf15p35MteURB62fkY6EQ	XS0272770396	99.166	2006-10-27	2016-10-27	100	EUR	\N	\N	99.16600000	100.00000000
kWjWrwfrNsSoZ71OVmeh-w	2011-10-15 18:54:56.348575	\N	2011-10-21 15:22:24.527411	\N	BTP-01LG 2012 2,50%	Cxf15p35MteURB62fkY6EQ	IT0004508971	100.150	2009-09-01	2012-07-01	100	EUR	\N	\N	100.15000000	100.00000000
llNwe6XQNNeKww1fBDmKrg	2011-10-15 18:58:27.782768	\N	2011-10-21 15:22:34.408223	\N	BTP-15ST14 2,15% IND	Cxf15p35MteURB62fkY6EQ	IT0003625909	99.051	2003-09-15	2014-09-15	100	EUR	\N	\N	99.05100000	100.00000000
lrJ031XIMtKAnOsECMQQ-Q	2011-10-15 19:13:07.907996	\N	2011-10-21 15:22:48.382791	\N	THYSSENKRUPP 8% 2014	Cxf15p35MteURB62fkY6EQ	DE000A0Z12Y2	99.071	2009-06-18	2014-06-18	100	EUR	\N	\N	99.07100000	100.00000000
oUXgaHbSMIeKouHWG2Er5A	2011-10-15 19:03:54.896422	\N	2011-10-21 15:23:12.955794	\N	CCT-LG09/16 TV	Cxf15p35MteURB62fkY6EQ	IT0004518715	97.650	2009-07-01	2016-07-01	100	EUR	\N	\N	97.65000000	100.00000000
qzUqIWQINU-4t3Yp_sJRpA	2011-10-18 19:27:20.846734	\N	2011-10-21 15:23:20.839058	\N	BANCA IMI TV MIN MAX 18/12/2016	Cxf15p35MteURB62fkY6EQ	XS0460430142	97	2010-12-18	2016-12-18	100	EUR	\N	\N	97.00000000	100.00000000
sZ0G6sK0PgeyUfIqO3ZDoA	2011-10-15 18:49:31.420429	\N	2011-10-21 15:23:35.593409	\N	BRITISH T 6,125% 14	Cxf15p35MteURB62fkY6EQ	XS0433216339	99.87	2009-07-11	2014-07-11	100	EUR	\N	\N	99.87000000	100.00000000
usAuGiiuOYa-nuQfYq7sXA	2011-10-18 19:31:13.306853	\N	2011-10-21 15:23:53.421481	\N	BANCA INTESA FR/11	Cxf15p35MteURB62fkY6EQ	XS0240017334	100.00	2005-12-30	2010-12-30	100.00	EUR	\N	\N	100.00000000	100.00000000
v-pSCex0OxyfYYQd_prg-g	2011-10-15 18:19:34.950616	\N	2011-10-21 15:24:02.814449	\N	Centrob 10/16 3,15%	Cxf15p35MteURB62fkY6EQ	IT0004568371	100	2010-02-26	2016-02-26	100	EUR	\N	\N	100.00000000	100.00000000
vfm3jBeuNVCpMIMZ-RBU2w	2011-10-15 18:53:37.453276	\N	2011-10-21 15:24:13.74885	\N	BOT-28FB11 SEM	4w1Izg94OQmTj3xUOTWK4g	IT0004629637	99.521	2010-09-01	2011-02-28	100	EUR	\N	\N	99.52100000	100.00000000
S6InmMwEMj6eSzHk5ZKEGw	2011-10-18 19:37:25.282714	\N	2011-10-18 19:37:25.282775	\N	ETF LYXOR EURO STOXX	dGcVW7y-NlCrWbTAGGUpFQ	FR0007054358	\N	\N	\N	\N	EUR	\N	\N	\N	\N
Abn1BWm3NpaLWlZ44HSSow	2011-10-18 19:37:38.934652	\N	2011-10-18 19:37:38.934712	\N	LYXOR ETF CAC 40	dGcVW7y-NlCrWbTAGGUpFQ	FR0007052782	\N	\N	\N	\N	EUR	\N	\N	\N	\N
B84WrpLBPnSD_xq_UFjQRg	2011-10-18 19:37:51.180341	\N	2011-10-18 19:37:51.180402	\N	ETF ISHARES S P 500	dGcVW7y-NlCrWbTAGGUpFQ	IE0031442068	\N	\N	\N	\N	EUR	\N	\N	\N	\N
_4-FrX5dNCyP2OqntwkoJw	2011-10-18 19:38:05.366501	\N	2011-10-18 19:38:05.366562	\N	ETF ISHARES II EURO	dGcVW7y-NlCrWbTAGGUpFQ	IE0008471009	\N	\N	\N	\N	EUR	\N	\N	\N	\N
WpcfBGi-MQyE74jolhZD5A	2011-10-18 19:38:24.440094	\N	2011-10-18 19:38:24.440154	\N	INVESCO US VALUE EQU	dGcVW7y-NlCrWbTAGGUpFQ	LU0511398793	\N	\N	\N	\N	EUR	\N	\N	\N	\N
mpANgTEfNF-8keCVUS6_Og	2011-10-18 19:38:49.207557	\N	2011-10-18 19:38:49.207649	\N	JB JAPAN STOCK	dGcVW7y-NlCrWbTAGGUpFQ	LU0099405374	\N	\N	\N	\N	JPY	\N	\N	\N	\N
jIbPyxoTMd6BA2_g1nHzpw	2011-10-18 19:39:07.489708	\N	2011-10-18 19:39:07.48977	\N	PICTET JAPAN INDEX C	dGcVW7y-NlCrWbTAGGUpFQ	LU0328684104	\N	\N	\N	\N	JPY	\N	\N	\N	\N
-_fNuDA1PO21CM0LKIgtFA	2011-10-15 18:33:42.645766	\N	2011-10-21 14:38:37.459978	\N	ITALEASE  06/11 EM.MK	Cxf15p35MteURB62fkY6EQ	IT0003977631	100	2006-01-30	2011-01-30	100	EUR	\N	\N	100.00000000	100.00000000
1GVozbpmMSSvn5uRN7Td4Q	2011-10-15 18:35:55.648039	\N	2011-10-21 14:39:30.918383	\N	Merrill 12 comm 70eu	Cxf15p35MteURB62fkY6EQ	XS0278244552	100	2007-01-04	2012-01-04	100	EUR	\N	\N	100.00000000	100.00000000
7mCV9QpoMSWauB6kJXBmPQ	2011-10-15 19:04:56.333699	\N	2011-10-21 14:40:27.553458	\N	CTZ-30ST11 24M	4w1Izg94OQmTj3xUOTWK4g	IT0004536931	97.257	2009-10-01	2011-09-30	100	EUR	\N	\N	97.26000000	100.00000000
L0f42PLcOOmdra-CZpJYYQ	2011-10-15 18:15:42.118403	\N	2011-10-21 14:42:46.311381	\N	CENTR.CA 9/14 3,6%	Cxf15p35MteURB62fkY6EQ	IT0004463334	100	2009-04-30	2014-04-30	100	EUR	\N	\N	100.00000000	100.00000000
TToW6U9pPuGrDklR_6hxNQ	2011-10-15 19:07:26.565825	\N	2011-10-21 14:46:29.670973	\N	FIAT FIN. 11 6,75%	Cxf15p35MteURB62fkY6EQ	XS0129648621	99.575	2001-05-25	2011-05-25	100	EUR	\N	\N	99.57500000	100.00000000
Y1xn-iSdM8iMTv5XNl9duQ	2011-10-18 19:33:34.561845	\N	2011-10-21 15:18:23.262073	\N	INTESA SANPAOLO 10/12 TV	Cxf15p35MteURB62fkY6EQ	IT0004621303	100	2010-08-03	2012-08-03	100	EUR	\N	\N	100.00000000	100.00000000
dgU-Yb_sPvSm6S1WZj0GOQ	2011-10-15 19:06:50.516483	\N	2011-10-21 15:20:49.465148	\N	ENEL 2007-2015 T.V.	Cxf15p35MteURB62fkY6EQ	IT0004292691	100.000	2007-01-14	2015-01-14	100.000	EUR	\N	\N	100.00000000	100.00000000
go01vXhyNjG3uUkEhPilfA	2011-10-15 18:05:59.634664	\N	2011-10-21 15:21:33.186559	\N	ABN AMRO HYBRID	Cxf15p35MteURB62fkY6EQ	IT0006639972	100	2007-02-27	2012-02-27	100	EUR	\N	\N	100.00000000	100.00000000
nvW9I3LrN_qKdpqOEaUgjA	2011-10-15 19:00:25.525185	\N	2011-10-21 15:23:03.276605	\N	BTP-15ST19 2,35% IND	Cxf15p35MteURB62fkY6EQ	IT0004380546	99.786	2008-03-15	2019-09-15	100	EUR	\N	\N	99.78600000	100.00000000
xEx6EnUHPLWgXCA1jdZOlQ	2011-10-15 17:51:46.314507	\N	2011-10-21 15:24:26.777724	\N	BTP 3,75% 05-01/08/15	Cxf15p35MteURB62fkY6EQ	IT0004220627	102	2005-08-01	2015-08-01	101.79	EUR	\N	\N	102.00000000	101.79000000
vWHnUYb_N96jNk1Wq6bkGQ	2011-10-22 17:37:48.188825	\N	2011-10-22 17:37:48.188902	2545131	ABB intl Fin ltd 4,5/8 % Notes 2006/6-6-13	Cxf15p35MteURB62fkY6EQ	XS0252915813	\N	2006-06-06	2013-06-06	\N	EUR	\N	\N	99.27600000	100.00000000
0z5zu5p0OQCiGQlG3oDuEQ	2011-10-22 17:39:52.482278	\N	2011-10-22 17:39:52.482341	11166903	Abengoa 8 1/2% 2010-31-1-16	Cxf15p35MteURB62fkY6EQ	XS0498817542	\N	2010-09-13	2016-09-13	\N	EUR	\N	\N	99.54400000	100.00000000
TJKmUX09MhSAzRDWmrl6kg	2011-10-22 17:41:34.14557	\N	2011-10-22 17:41:34.145644	2763356	Abu Dhabi Nat Energy 4 3/8%  2006-28,10,13 RegS	Cxf15p35MteURB62fkY6EQ	XS0272947150	\N	2006-10-28	2013-10-28	\N	EUR	\N	\N	99.35700000	100.00000000
3mnOiGuCNkKywXU0j_QM4w	2011-10-22 17:45:04.849415	\N	2011-10-22 17:46:09.672614	2872727	Aegon Global Inst 4,25% Global	Cxf15p35MteURB62fkY6EQ	XS0282614204	\N	2008-01-23	2012-01-23	\N	EUR	\N	\N	99.80600000	100.00000000
_MgesvPiOn2kF5diBUw38A	2011-10-22 17:53:29.057647	\N	2011-10-22 17:53:38.86678	10604824	Allied Irish Banks 4,1/2% 2009-1-10-12	Cxf15p35MteURB62fkY6EQ	XS0455308923	\N	2009-10-01	2012-10-01	\N	EUR	\N	\N	99.76100000	100.00000000
QQfQfKEXM6CMCDGKvCSgaQ	2011-10-22 17:54:28.515013	\N	2011-10-22 17:54:28.515093	11213470	Ang.Ire 8K Corp 4%	Cxf15p35MteURB62fkY6EQ	XS0502258790	\N	2010-04-15	2015-04-15	\N	EUR	\N	\N	99.72400000	100.00000000
SjePCFeGMrmlR373YKfJEw	2011-10-22 17:55:25.621627	\N	2011-10-22 17:55:25.621693	3102200	ANZBanking Group 4,3/8 %	Cxf15p35MteURB62fkY6EQ	XS0300682621	\N	2007-05-24	2012-05-24	\N	EUR	\N	\N	99.57400000	100.00000000
xIHdzmE0MgSuTWXpn0NNNQ	2011-10-22 17:56:24.053386	\N	2011-10-22 17:56:24.053448	1201121	ASIF III 5,5% Notes Reg S	Cxf15p35MteURB62fkY6EQ	XS0125622927	\N	2001-03-07	2011-03-07	\N	EUR	\N	\N	99.69900000	100.00000000
c40X_o-xPWOGpesvjw-PvQ	2011-10-22 17:58:06.390935	\N	2011-10-22 17:58:06.390997	2891548	Bank of America 4,45%EMTN 2007-31-1-14 Senior	Cxf15p35MteURB62fkY6EQ	XS0284283081	\N	2007-01-31	2014-01-31	\N	EUR	\N	\N	99.87600000	100.00000000
2wrZr4p9NHOt3bkytUzpZg	2011-10-22 17:59:03.376837	\N	2011-10-22 17:59:03.3769	2898569	Bank of Scot 4,1/8% 2007/6-2-2012	Cxf15p35MteURB62fkY6EQ	XS0284896767	\N	2007-02-06	2012-02-06	\N	EUR	\N	\N	99.45200000	100.00000000
WiaNyGuvMSuLqfTuhjXnwA	2011-10-22 18:00:13.735037	\N	2011-10-22 18:00:13.735102	1792959	BAWAG P.S.K 4 1/4%	Cxf15p35MteURB62fkY6EQ	XS0186452974	\N	2004-02-18	2014-02-18	\N	EUR	\N	\N	99.14000000	100.00000000
sG_5qs0UOumJJjZSuOVfWg	2011-10-22 18:01:09.539187	\N	2011-10-22 18:01:09.53925	1852033	Bayerische Ldbk 4% 2004-5-5-2011	Cxf15p35MteURB62fkY6EQ	XS0191946390	\N	2004-05-05	2011-05-05	\N	EUR	\N	\N	99.78400000	100.00000000
vf0huLpDOJa9JG_o0l0h0Q	2011-10-22 18:01:55.29119	\N	2011-10-22 18:01:55.291294	3703561	Bco Espirito Santo 4 3/8%	Cxf15p35MteURB62fkY6EQ	PTBERU1E0015	\N	2008-01-25	2011-01-25	\N	EUR	\N	\N	99.99000000	100.00000000
gyLViofrMMa58NohlkRwMg	2011-10-22 18:02:53.072854	\N	2011-10-22 18:02:53.072917	10255647	Bco Santander Totta 3 3/4% 2009-12-6-12	Cxf15p35MteURB62fkY6EQ	PTCPP4OM0023	\N	2009-06-12	2012-06-12	\N	EUR	\N	\N	100.00000000	100.00000000
w6jhUFd3OhONhWthabxdSg	2011-10-22 18:03:24.498583	\N	2011-10-22 18:03:24.498646	10259365	BCP 3 3/4 % 2009- 17 -6 - 11	Cxf15p35MteURB62fkY6EQ	PTBCLSOE0018	\N	2009-06-17	2011-06-17	\N	EUR	\N	\N	100.00000000	100.00000000
GJqrGDJBNSKmxfxeHRw29w	2011-10-22 18:04:03.002434	\N	2011-10-22 18:04:03.002521	1233519	BES Finance 6 1/4% 2001-17-5-11 S13sub	Cxf15p35MteURB62fkY6EQ	XS0129239454	\N	2001-05-17	2011-05-17	\N	EUR	\N	\N	99.32600000	100.00000000
uM6YZeQPPdOE7sHEs4hAQQ	2011-10-22 18:08:27.747302	\N	2011-10-22 18:08:27.747365	10070389	BHP Billiton Fion. 4 3/4% 2009-4-4-12	Cxf15p35MteURB62fkY6EQ	XS0421249078	\N	2009-04-04	2012-04-04	\N	EUR	\N	\N	99.75500000	100.00000000
j1HzIxDQOUaNtiDudWYHYw	2011-10-22 18:09:05.151561	\N	2011-10-22 18:09:05.151624	2320879	CADES 3 1/4% Notes	Cxf15p35MteURB62fkY6EQ	FR0010249763	\N	2005-04-25	2013-04-25	\N	EUR	\N	\N	99.82300000	100.00000000
SR2vcstONwCtWPjOEgN5Zg	2011-10-22 18:10:02.167791	\N	2011-10-22 18:10:02.167872	2696359	Commerzbank 2006 - 13.9.16	Cxf15p35MteURB62fkY6EQ	DE000CB07899	\N	2006-09-13	2016-09-13	\N	EUR	\N	\N	99.54400000	100.00000000
9nWjzXsvPTuF7azTMoQ-7A	2011-10-22 18:11:40.575367	\N	2011-10-22 18:11:40.57543	1778817	Calyon Fin Prod Euro	Cxf15p35MteURB62fkY6EQ	XS0184866282	\N	2004-04-29	2011-04-29	\N	EUR	\N	\N	96.35000000	100.00000000
36uHfNUHM_y3Po7rCPaY-g	2011-10-22 18:13:06.546482	\N	2011-10-22 18:13:06.546546	10510009	Croatian Bank 7 1/4%  2009-3-9-12	Cxf15p35MteURB62fkY6EQ	XS0449738987	\N	2009-09-03	2012-09-03	\N	EUR	\N	\N	100.00000000	100.00000000
vAdaP3pMNE6Qeg3tn-Zjpg	2011-10-22 18:13:42.531963	\N	2011-10-22 18:13:42.532026	3781199	Danske Bank 2008-18.8.14	Cxf15p35MteURB62fkY6EQ	XS0346728065	\N	2008-08-18	2014-08-18	\N	EUR	\N	\N	99.84500000	100.00000000
Qy7yurZqNJ2Rn5S9pFy-_Q	2011-10-22 18:14:40.434886	\N	2011-10-22 18:14:40.434962	2481848	Depfa ACS 3 1/2% 2006-16-3-11	Cxf15p35MteURB62fkY6EQ	DE000A0GPMR2	\N	2006-03-16	2011-03-16	\N	EUR	\N	\N	99.70300000	100.00000000
OqJ5Gu7gMCO_-TuhFREj3A	2011-10-22 18:15:35.258624	\N	2011-10-22 18:15:35.258687	1612660	Depfa ACS 3,7/8% 2003-15-7-13	Cxf15p35MteURB62fkY6EQ	DE0007009482	\N	2003-07-15	2013-07-15	\N	EUR	\N	\N	99.48800000	100.00000000
W4VFPJdcNcOTsi-ura1MSA	2011-10-22 18:16:41.329531	\N	2011-10-22 18:16:41.329594	2902963	Dubai Hldg 4 3/4% 2007-31-1-14	Cxf15p35MteURB62fkY6EQ	XS0285303821	\N	2007-01-30	2014-01-30	\N	EUR	\N	\N	99.67400000	100.00000000
BLLu85lWMfS7dhigR9rfrg	2011-10-22 18:17:39.015195	\N	2011-10-22 18:17:39.015261	1623802	EIB 3 5/8% Global notes	Cxf15p35MteURB62fkY6EQ	XS0170558877	\N	2003-10-15	2013-10-15	\N	EUR	\N	\N	99.32100000	100.00000000
gGRhjufvObeIs0FehtPFog	2011-10-22 18:18:49.329012	\N	2011-10-22 18:18:49.329092	10907152	FIAT Fin Tra 5,3/4% notes	Cxf15p35MteURB62fkY6EQ	XS0474906699	\N	2009-12-18	2012-12-18	\N	EUR	\N	\N	102.17200000	100.00000000
964xRQSYMBujjgzgc5YYeQ	2011-10-22 18:20:08.201353	\N	2011-10-22 18:20:08.201426	3681565	GE Cap Europ Funding 4,3/49   2008-18-1-11	Cxf15p35MteURB62fkY6EQ	XS0340179307	\N	2008-01-18	2011-01-18	\N	EUR	\N	\N	101.06600000	100.00000000
gTiVdZK5OLO8a5ekg8ouTw	2011-10-22 18:20:48.269196	\N	2011-10-22 18:20:48.269262	1701431	GE Europ Fundin 4,5/8 2003/29-10-13	Cxf15p35MteURB62fkY6EQ	XS0178807649	\N	2003-10-29	2013-10-29	\N	EUR	\N	\N	99.80400000	100.00000000
Q8502vQvORO5On-K3_vr7Q	2011-10-22 18:22:06.067825	\N	2011-10-22 18:22:56.253505	2592655	Generali Finance BV Global Notes Perp	Cxf15p35MteURB62fkY6EQ	XS0256975458	\N	2006-06-16	2999-06-16	\N	EUR	\N	\N	100.00000000	100.00000000
McLZsEAfPaOkHxZpSvMm2A	2011-10-22 18:23:38.149463	\N	2011-10-22 18:23:38.149544	11117819	Gldm Saxhs Grp 4 3/8  2010-16-3-17	Cxf15p35MteURB62fkY6EQ	XS0494996043	\N	2010-03-16	2017-03-16	\N	EUR	\N	\N	99.42200000	100.00000000
O3MFw9eHPXqZc1qXPrwE1g	2011-10-22 18:24:30.265944	\N	2011-10-22 18:24:30.266006	\N	Goldman Sachs Group  4% Reg	Cxf15p35MteURB62fkY6EQ	XS0211034540	\N	2005-02-02	2015-02-02	\N	EUR	\N	\N	99.28100000	100.00000000
lEWgXNo5OLi1AZ732oNOUw	2011-10-22 18:25:19.512202	\N	2011-10-22 18:25:19.512269	1576430	HBOS 4 7/8 %  Notes	Cxf15p35MteURB62fkY6EQ	XS0165449736	\N	2003-03-20	2015-03-20	\N	EUR	\N	\N	99.64400000	100.00000000
DnYkaS7aPj6VIbmF41h9-Q	2011-10-22 18:26:06.155447	\N	2011-10-22 18:26:06.155548	1498424	ING Bank 5 1/4% 2002-4-1-13	Cxf15p35MteURB62fkY6EQ	NL0000113140	\N	2002-01-04	2013-01-04	\N	EUR	\N	\N	100.92400000	100.00000000
KPqTybwhMVKT8hNrnR46IQ	2011-10-22 18:27:24.224669	\N	2011-10-22 18:27:24.224731	10897465	Intesa Sanpaolo 3 3/8% GMTN	Cxf15p35MteURB62fkY6EQ	XS0478285389	\N	2010-01-19	2015-01-19	\N	EUR	\N	\N	99.96800000	100.00000000
bzZJOf1tMHebTvfbOEGw8g	2011-10-22 18:28:00.355748	\N	2011-10-22 18:28:00.355812	1187313	Irish Life &amp; perm 6,1/4&amp; 2001-15-2-11	Cxf15p35MteURB62fkY6EQ	XS0124072389	\N	2001-02-15	2011-02-15	\N	EUR	\N	\N	101.17400000	100.00000000
I7Ql429aPQC4801Xuf1y-A	2011-10-22 18:28:47.465453	\N	2011-10-22 18:28:47.465517	10553559	KBC Ifima NV 41/2%Fixes	Cxf15p35MteURB62fkY6EQ	XS0452462723	\N	2009-09-17	2014-09-17	\N	EUR	\N	\N	99.93400000	100.00000000
45JA5JTkNf-ufzseYAODng	2011-10-22 18:29:28.924132	\N	2011-10-22 18:29:28.924195	1562769	Lbk Hessen-Thuering 4 1/4%	Cxf15p35MteURB62fkY6EQ	XS0163686529	\N	2003-03-05	2013-03-05	\N	EUR	\N	\N	99.28200000	100.00000000
ztzzwgpCNl6cP4PlgrpOqQ	2011-10-22 18:30:24.773446	\N	2011-10-22 18:30:24.77351	10759348	Lloyds TSB 3 1/4 % EMTN Reg-S	Cxf15p35MteURB62fkY6EQ	XS0469192388	\N	2009-11-26	2012-11-26	\N	EUR	\N	\N	99.68300000	100.00000000
7O7oajsGNYySvhRuRSL2Dg	2011-10-22 18:31:01.418937	\N	2011-10-22 18:31:01.419	3037396	Merril Lymch 3 1/2% Regd	Cxf15p35MteURB62fkY6EQ	XS0286930952	\N	2007-03-31	2013-03-30	\N	EUR	\N	\N	100.00000000	100.00000000
3vCrUyiVN1SYFJHsC-Mk2A	2011-10-22 18:31:53.352661	\N	2011-10-22 18:31:53.352724	10686852	Morgan Stanley 4 1/2% 2009-29-10-14 Senior	Cxf15p35MteURB62fkY6EQ	XS0461758830	\N	2009-10-29	2014-10-29	\N	EUR	\N	\N	99.63200000	100.00000000
Xzg3a659N7aKFLObgyYlOg	2011-10-22 18:36:20.599744	\N	2011-10-22 18:36:20.599807	2335299	Rentenanstalt Fiduciary Notes 2005-perp VRN Reg-S sub	Cxf15p35MteURB62fkY6EQ	XS0235535035	\N	2005-11-16	2999-11-16	\N	EUR	\N	\N	100.00000000	100.00000000
t6PDGdB7MEqB3IMKkhDn8A	2011-10-22 18:37:50.485355	\N	2011-10-22 18:37:50.48542	4475318	Roche Hold 4,625%(no min) 2009-4-3-13	Cxf15p35MteURB62fkY6EQ	XS0415624393	\N	2011-03-04	2013-03-04	\N	EUR	\N	\N	99.57200000	100.00000000
dWw5bKeGP-KyLJATzaZ-xw	2011-10-22 18:38:28.885507	\N	2011-10-22 18:38:28.885571	3064757	Toyota Motor Credit 4 1/4%  07-2-5-12	Cxf15p35MteURB62fkY6EQ	XS0297396508	\N	2007-05-02	2012-05-02	\N	EUR	\N	\N	101.42500000	100.00000000
QaJxwAzyOweHA3uQ7NVSCQ	2011-10-22 18:39:08.460111	\N	2011-10-22 18:39:08.460235	2765176	Yorkshire Building 4%	Cxf15p35MteURB62fkY6EQ	XS0273120716	\N	2006-11-07	2011-11-07	\N	EUR	\N	\N	99.99100000	100.00000000
rntPm4VYNXGXT85HtWO5-Q	2011-10-22 18:39:47.34657	\N	2011-10-22 18:39:47.346635	10109851	Zurich Finance  4 7/8 % 2009-14-4-12	Cxf15p35MteURB62fkY6EQ	XS0423888824	\N	2009-04-14	2012-04-14	\N	EUR	\N	\N	99.68700000	100.00000000
yurLlvsrNe6PUdRRitg7Pg	2011-10-22 18:40:30.391508	\N	2011-10-22 18:40:30.391579	721084	Deka-EuropaBond TF	dGcVW7y-NlCrWbTAGGUpFQ	DE0009771980	\N	\N	\N	\N	EUR	\N	\N	\N	\N
UXYVaE3cPoK15vXvDKFndw	2011-10-22 18:40:56.521521	\N	2011-10-22 18:41:37.872169	10175424	PLATINUM All Star Fund	dGcVW7y-NlCrWbTAGGUpFQ	KYG7126M1731	\N	\N	\N	\N	EUR	\N	\N	\N	\N
\.


--
-- Data for Name: genrotit_userobject; Type: TABLE DATA; Schema: genrotit; Owner: postgres
--

COPY genrotit_userobject (id, __ins_ts, __del_ts, __mod_ts, code, objtype, pkg, tbl, userid, description, notes, data, authtags, private, quicklist, flags) FROM stdin;
\.


--
-- Data for Name: genrotit_valuta; Type: TABLE DATA; Schema: genrotit; Owner: postgres
--

COPY genrotit_valuta (__ins_ts, __del_ts, __mod_ts, codice, descrizione) FROM stdin;
2011-10-18 14:27:52.390347	\N	2011-10-18 14:27:52.390408	EUR	Euro
2011-10-18 19:23:29.185596	\N	2011-10-18 19:23:29.185659	USD	Dollaro USA
2011-10-18 19:24:03.937249	\N	2011-10-18 19:24:03.937311	JPY	Yen giapponese
2011-10-18 19:24:14.238737	\N	2011-10-18 19:24:14.238799	CHF	Franco svizzero
2011-10-18 19:24:25.996802	\N	2011-10-18 19:24:25.99689	GBP	Sterlina inglese
\.


--
-- Data for Name: genrotit_valuta_storico; Type: TABLE DATA; Schema: genrotit; Owner: postgres
--

COPY genrotit_valuta_storico (id, __ins_ts, __del_ts, __mod_ts, valuta_codice, data, valore) FROM stdin;
\.


--
-- Data for Name: genrotit_valutazione; Type: TABLE DATA; Schema: genrotit; Owner: postgres
--

COPY genrotit_valutazione ("V", id, __ins_ts, __del_ts, __mod_ts, data_valutazione, prezzo, corso, titolo_id) FROM stdin;
\.


SET search_path = glbl, pg_catalog;

--
-- Data for Name: glbl_counter; Type: TABLE DATA; Schema: glbl; Owner: postgres
--

COPY glbl_counter (__ins_ts, __del_ts, __mod_ts, codekey, code, pkg, name, counter, last_used, holes) FROM stdin;
\.


--
-- Data for Name: glbl_localita; Type: TABLE DATA; Schema: glbl; Owner: postgres
--

COPY glbl_localita (id, nome, provincia, codice_istat, codice_comune, prefisso_tel, cap) FROM stdin;
\.


--
-- Data for Name: glbl_nazione; Type: TABLE DATA; Schema: glbl; Owner: postgres
--

COPY glbl_nazione (code, name, code3, nmbr) FROM stdin;
\.


--
-- Data for Name: glbl_provincia; Type: TABLE DATA; Schema: glbl; Owner: postgres
--

COPY glbl_provincia (sigla, regione, nome, codice_istat, ordine, ordine_tot, cap_valido, auxdata) FROM stdin;
\.


--
-- Data for Name: glbl_regione; Type: TABLE DATA; Schema: glbl; Owner: postgres
--

COPY glbl_regione (sigla, nome, codice_istat, ordine, zona) FROM stdin;
\.


--
-- Data for Name: glbl_stradario_cap; Type: TABLE DATA; Schema: glbl; Owner: postgres
--

COPY glbl_stradario_cap (id, cap, provincia, comune, comune2, frazione, frazione2, topo, topo2, pref, n_civico) FROM stdin;
\.


--
-- Data for Name: glbl_userobject; Type: TABLE DATA; Schema: glbl; Owner: postgres
--

COPY glbl_userobject (id, __ins_ts, __del_ts, __mod_ts, code, objtype, pkg, tbl, userid, description, notes, data, authtags, private, quicklist, flags) FROM stdin;
\.


SET search_path = sys, pg_catalog;

--
-- Data for Name: sys_counter; Type: TABLE DATA; Schema: sys; Owner: postgres
--

COPY sys_counter (__ins_ts, __del_ts, __mod_ts, codekey, code, pkg, name, counter, last_used, holes) FROM stdin;
\.


--
-- Data for Name: sys_external_token; Type: TABLE DATA; Schema: sys; Owner: postgres
--

COPY sys_external_token (id, datetime, expiry, allowed_user, connection_id, max_usages, allowed_host, page_path, method, parameters, exec_user) FROM stdin;
\.


--
-- Data for Name: sys_external_token_use; Type: TABLE DATA; Schema: sys; Owner: postgres
--

COPY sys_external_token_use (id, external_token_id, datetime, host) FROM stdin;
\.


--
-- Data for Name: sys_locked_record; Type: TABLE DATA; Schema: sys; Owner: postgres
--

COPY sys_locked_record (id, lock_ts, lock_table, lock_pkey, page_id, connection_id, username) FROM stdin;
\.


--
-- Data for Name: sys_message; Type: TABLE DATA; Schema: sys; Owner: postgres
--

COPY sys_message (id, datetime, expiry, dst_page_id, dst_user, dst_connection_id, src_page_id, src_user, src_connection_id, message_type, body) FROM stdin;
\.


--
-- Data for Name: sys_userobject; Type: TABLE DATA; Schema: sys; Owner: postgres
--

COPY sys_userobject (id, __ins_ts, __del_ts, __mod_ts, code, objtype, pkg, tbl, userid, description, notes, data, authtags, private, quicklist, flags) FROM stdin;
\.


SET search_path = test15, pg_catalog;

--
-- Data for Name: test15_counter; Type: TABLE DATA; Schema: test15; Owner: postgres
--

COPY test15_counter (__ins_ts, __del_ts, __mod_ts, codekey, code, pkg, name, counter, last_used, holes) FROM stdin;
\.


--
-- Data for Name: test15_recursive; Type: TABLE DATA; Schema: test15; Owner: postgres
--

COPY test15_recursive (id, __ins_ts, __del_ts, __mod_ts, code, description, parent_id) FROM stdin;
\.


--
-- Data for Name: test15_userobject; Type: TABLE DATA; Schema: test15; Owner: postgres
--

COPY test15_userobject (id, __ins_ts, __del_ts, __mod_ts, code, objtype, pkg, tbl, userid, description, notes, data, authtags, private, quicklist, flags) FROM stdin;
\.


SET search_path = adm, pg_catalog;

--
-- Name: adm_audit_pkey; Type: CONSTRAINT; Schema: adm; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adm_audit
    ADD CONSTRAINT adm_audit_pkey PRIMARY KEY (id);


--
-- Name: adm_authorization_pkey; Type: CONSTRAINT; Schema: adm; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adm_authorization
    ADD CONSTRAINT adm_authorization_pkey PRIMARY KEY (code);


--
-- Name: adm_connection_pkey; Type: CONSTRAINT; Schema: adm; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adm_connection
    ADD CONSTRAINT adm_connection_pkey PRIMARY KEY (id);


--
-- Name: adm_counter_pkey; Type: CONSTRAINT; Schema: adm; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adm_counter
    ADD CONSTRAINT adm_counter_pkey PRIMARY KEY (codekey);


--
-- Name: adm_datacatalog_pkey; Type: CONSTRAINT; Schema: adm; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adm_datacatalog
    ADD CONSTRAINT adm_datacatalog_pkey PRIMARY KEY (id);


--
-- Name: adm_doctemplate_name_key; Type: CONSTRAINT; Schema: adm; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adm_doctemplate
    ADD CONSTRAINT adm_doctemplate_name_key UNIQUE (name);


--
-- Name: adm_doctemplate_pkey; Type: CONSTRAINT; Schema: adm; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adm_doctemplate
    ADD CONSTRAINT adm_doctemplate_pkey PRIMARY KEY (id);


--
-- Name: adm_htag_pkey; Type: CONSTRAINT; Schema: adm; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adm_htag
    ADD CONSTRAINT adm_htag_pkey PRIMARY KEY (id);


--
-- Name: adm_htmltemplate_name_key; Type: CONSTRAINT; Schema: adm; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adm_htmltemplate
    ADD CONSTRAINT adm_htmltemplate_name_key UNIQUE (name);


--
-- Name: adm_htmltemplate_pkey; Type: CONSTRAINT; Schema: adm; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adm_htmltemplate
    ADD CONSTRAINT adm_htmltemplate_pkey PRIMARY KEY (id);


--
-- Name: adm_menu_code_key; Type: CONSTRAINT; Schema: adm; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adm_menu
    ADD CONSTRAINT adm_menu_code_key UNIQUE (code);


--
-- Name: adm_menu_pkey; Type: CONSTRAINT; Schema: adm; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adm_menu
    ADD CONSTRAINT adm_menu_pkey PRIMARY KEY (id);


--
-- Name: adm_permission_pkey; Type: CONSTRAINT; Schema: adm; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adm_permission
    ADD CONSTRAINT adm_permission_pkey PRIMARY KEY (id);


--
-- Name: adm_preference_pkey; Type: CONSTRAINT; Schema: adm; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adm_preference
    ADD CONSTRAINT adm_preference_pkey PRIMARY KEY (code);


--
-- Name: adm_record_tag_pkey; Type: CONSTRAINT; Schema: adm; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adm_record_tag
    ADD CONSTRAINT adm_record_tag_pkey PRIMARY KEY (id);


--
-- Name: adm_served_page_pkey; Type: CONSTRAINT; Schema: adm; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adm_served_page
    ADD CONSTRAINT adm_served_page_pkey PRIMARY KEY (page_id);


--
-- Name: adm_tag_pkey; Type: CONSTRAINT; Schema: adm; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adm_tag
    ADD CONSTRAINT adm_tag_pkey PRIMARY KEY (id);


--
-- Name: adm_user_pkey; Type: CONSTRAINT; Schema: adm; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adm_user
    ADD CONSTRAINT adm_user_pkey PRIMARY KEY (id);


--
-- Name: adm_user_tag_pkey; Type: CONSTRAINT; Schema: adm; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adm_user_tag
    ADD CONSTRAINT adm_user_tag_pkey PRIMARY KEY (id);


--
-- Name: adm_user_username_key; Type: CONSTRAINT; Schema: adm; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adm_user
    ADD CONSTRAINT adm_user_username_key UNIQUE (username);


--
-- Name: adm_userobject_pkey; Type: CONSTRAINT; Schema: adm; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY adm_userobject
    ADD CONSTRAINT adm_userobject_pkey PRIMARY KEY (id);


SET search_path = genrotit, pg_catalog;

--
-- Name: genrotit_area_geografica_pkey; Type: CONSTRAINT; Schema: genrotit; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY genrotit_area_geografica
    ADD CONSTRAINT genrotit_area_geografica_pkey PRIMARY KEY (id);


--
-- Name: genrotit_banca_pkey; Type: CONSTRAINT; Schema: genrotit; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY genrotit_banca
    ADD CONSTRAINT genrotit_banca_pkey PRIMARY KEY (id);


--
-- Name: genrotit_campo_pkey; Type: CONSTRAINT; Schema: genrotit; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY genrotit_campo
    ADD CONSTRAINT genrotit_campo_pkey PRIMARY KEY (id);


--
-- Name: genrotit_counter_pkey; Type: CONSTRAINT; Schema: genrotit; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY genrotit_counter
    ADD CONSTRAINT genrotit_counter_pkey PRIMARY KEY (codekey);


--
-- Name: genrotit_emittente_pkey; Type: CONSTRAINT; Schema: genrotit; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY genrotit_emittente
    ADD CONSTRAINT genrotit_emittente_pkey PRIMARY KEY (id);


--
-- Name: genrotit_gestione_pkey; Type: CONSTRAINT; Schema: genrotit; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY genrotit_gestione
    ADD CONSTRAINT genrotit_gestione_pkey PRIMARY KEY (id);


--
-- Name: genrotit_h_tipo_titolo_pkey; Type: CONSTRAINT; Schema: genrotit; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY genrotit_h_tipo_titolo
    ADD CONSTRAINT genrotit_h_tipo_titolo_pkey PRIMARY KEY (id);


--
-- Name: genrotit_movimento_pkey; Type: CONSTRAINT; Schema: genrotit; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY genrotit_movimento
    ADD CONSTRAINT genrotit_movimento_pkey PRIMARY KEY (id);


--
-- Name: genrotit_referente_pkey; Type: CONSTRAINT; Schema: genrotit; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY genrotit_referente
    ADD CONSTRAINT genrotit_referente_pkey PRIMARY KEY (id);


--
-- Name: genrotit_tipo_titolo_campo_pkey; Type: CONSTRAINT; Schema: genrotit; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY genrotit_tipo_titolo_campo
    ADD CONSTRAINT genrotit_tipo_titolo_campo_pkey PRIMARY KEY (id);


--
-- Name: genrotit_tipo_titolo_pkey; Type: CONSTRAINT; Schema: genrotit; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY genrotit_tipo_titolo
    ADD CONSTRAINT genrotit_tipo_titolo_pkey PRIMARY KEY (id);


--
-- Name: genrotit_titolo_pkey; Type: CONSTRAINT; Schema: genrotit; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY genrotit_titolo
    ADD CONSTRAINT genrotit_titolo_pkey PRIMARY KEY (id);


--
-- Name: genrotit_userobject_pkey; Type: CONSTRAINT; Schema: genrotit; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY genrotit_userobject
    ADD CONSTRAINT genrotit_userobject_pkey PRIMARY KEY (id);


--
-- Name: genrotit_valuta_pkey; Type: CONSTRAINT; Schema: genrotit; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY genrotit_valuta
    ADD CONSTRAINT genrotit_valuta_pkey PRIMARY KEY (codice);


--
-- Name: genrotit_valuta_storico_pkey; Type: CONSTRAINT; Schema: genrotit; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY genrotit_valuta_storico
    ADD CONSTRAINT genrotit_valuta_storico_pkey PRIMARY KEY (id);


--
-- Name: genrotit_valutazione_pkey; Type: CONSTRAINT; Schema: genrotit; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY genrotit_valutazione
    ADD CONSTRAINT genrotit_valutazione_pkey PRIMARY KEY (id);


SET search_path = glbl, pg_catalog;

--
-- Name: glbl_counter_pkey; Type: CONSTRAINT; Schema: glbl; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY glbl_counter
    ADD CONSTRAINT glbl_counter_pkey PRIMARY KEY (codekey);


--
-- Name: glbl_localita_pkey; Type: CONSTRAINT; Schema: glbl; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY glbl_localita
    ADD CONSTRAINT glbl_localita_pkey PRIMARY KEY (id);


--
-- Name: glbl_nazione_pkey; Type: CONSTRAINT; Schema: glbl; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY glbl_nazione
    ADD CONSTRAINT glbl_nazione_pkey PRIMARY KEY (code);


--
-- Name: glbl_provincia_pkey; Type: CONSTRAINT; Schema: glbl; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY glbl_provincia
    ADD CONSTRAINT glbl_provincia_pkey PRIMARY KEY (sigla);


--
-- Name: glbl_regione_pkey; Type: CONSTRAINT; Schema: glbl; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY glbl_regione
    ADD CONSTRAINT glbl_regione_pkey PRIMARY KEY (sigla);


--
-- Name: glbl_stradario_cap_pkey; Type: CONSTRAINT; Schema: glbl; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY glbl_stradario_cap
    ADD CONSTRAINT glbl_stradario_cap_pkey PRIMARY KEY (id);


--
-- Name: glbl_userobject_pkey; Type: CONSTRAINT; Schema: glbl; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY glbl_userobject
    ADD CONSTRAINT glbl_userobject_pkey PRIMARY KEY (id);


--
-- Name: un_glbl_glbl_localita_id; Type: CONSTRAINT; Schema: glbl; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY glbl_localita
    ADD CONSTRAINT un_glbl_glbl_localita_id UNIQUE (id);


SET search_path = sys, pg_catalog;

--
-- Name: sys_counter_pkey; Type: CONSTRAINT; Schema: sys; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY sys_counter
    ADD CONSTRAINT sys_counter_pkey PRIMARY KEY (codekey);


--
-- Name: sys_external_token_pkey; Type: CONSTRAINT; Schema: sys; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY sys_external_token
    ADD CONSTRAINT sys_external_token_pkey PRIMARY KEY (id);


--
-- Name: sys_external_token_use_pkey; Type: CONSTRAINT; Schema: sys; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY sys_external_token_use
    ADD CONSTRAINT sys_external_token_use_pkey PRIMARY KEY (id);


--
-- Name: sys_locked_record_pkey; Type: CONSTRAINT; Schema: sys; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY sys_locked_record
    ADD CONSTRAINT sys_locked_record_pkey PRIMARY KEY (id);


--
-- Name: sys_message_pkey; Type: CONSTRAINT; Schema: sys; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY sys_message
    ADD CONSTRAINT sys_message_pkey PRIMARY KEY (id);


--
-- Name: sys_userobject_pkey; Type: CONSTRAINT; Schema: sys; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY sys_userobject
    ADD CONSTRAINT sys_userobject_pkey PRIMARY KEY (id);


SET search_path = test15, pg_catalog;

--
-- Name: test15_counter_pkey; Type: CONSTRAINT; Schema: test15; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY test15_counter
    ADD CONSTRAINT test15_counter_pkey PRIMARY KEY (codekey);


--
-- Name: test15_recursive_pkey; Type: CONSTRAINT; Schema: test15; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY test15_recursive
    ADD CONSTRAINT test15_recursive_pkey PRIMARY KEY (id);


--
-- Name: test15_userobject_pkey; Type: CONSTRAINT; Schema: test15; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY test15_userobject
    ADD CONSTRAINT test15_userobject_pkey PRIMARY KEY (id);


SET search_path = adm, pg_catalog;

--
-- Name: adm_authorization_user_id_idx; Type: INDEX; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE INDEX adm_authorization_user_id_idx ON adm_authorization USING btree (user_id);


--
-- Name: adm_connection_userid_idx; Type: INDEX; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE INDEX adm_connection_userid_idx ON adm_connection USING btree (userid);


--
-- Name: adm_datacatalog_code_idx; Type: INDEX; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE INDEX adm_datacatalog_code_idx ON adm_datacatalog USING btree (code);


--
-- Name: adm_datacatalog_parent_code_idx; Type: INDEX; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE INDEX adm_datacatalog_parent_code_idx ON adm_datacatalog USING btree (parent_code);


--
-- Name: adm_doctemplate_name_idx; Type: INDEX; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX adm_doctemplate_name_idx ON adm_doctemplate USING btree (name);


--
-- Name: adm_htag_code_idx; Type: INDEX; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE INDEX adm_htag_code_idx ON adm_htag USING btree (code);


--
-- Name: adm_htag_parent_code_idx; Type: INDEX; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE INDEX adm_htag_parent_code_idx ON adm_htag USING btree (parent_code);


--
-- Name: adm_htmltemplate_name_idx; Type: INDEX; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX adm_htmltemplate_name_idx ON adm_htmltemplate USING btree (name);


--
-- Name: adm_menu_code_idx; Type: INDEX; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX adm_menu_code_idx ON adm_menu USING btree (code);


--
-- Name: adm_permission_datacatalog_id_idx; Type: INDEX; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE INDEX adm_permission_datacatalog_id_idx ON adm_permission USING btree (datacatalog_id);


--
-- Name: adm_permission_tag_id_idx; Type: INDEX; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE INDEX adm_permission_tag_id_idx ON adm_permission USING btree (tag_id);


--
-- Name: adm_served_page_connection_id_idx; Type: INDEX; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE INDEX adm_served_page_connection_id_idx ON adm_served_page USING btree (connection_id);


--
-- Name: adm_user_tag_tag_id_idx; Type: INDEX; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE INDEX adm_user_tag_tag_id_idx ON adm_user_tag USING btree (tag_id);


--
-- Name: adm_user_tag_user_id_idx; Type: INDEX; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE INDEX adm_user_tag_user_id_idx ON adm_user_tag USING btree (user_id);


--
-- Name: adm_user_username_idx; Type: INDEX; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX adm_user_username_idx ON adm_user USING btree (username);


--
-- Name: adm_userobject_code_idx; Type: INDEX; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE INDEX adm_userobject_code_idx ON adm_userobject USING btree (code);


--
-- Name: adm_userobject_description_idx; Type: INDEX; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE INDEX adm_userobject_description_idx ON adm_userobject USING btree (description);


--
-- Name: adm_userobject_objtype_idx; Type: INDEX; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE INDEX adm_userobject_objtype_idx ON adm_userobject USING btree (objtype);


--
-- Name: adm_userobject_userid_idx; Type: INDEX; Schema: adm; Owner: postgres; Tablespace: 
--

CREATE INDEX adm_userobject_userid_idx ON adm_userobject USING btree (userid);


SET search_path = genrotit, pg_catalog;

--
-- Name: genrotit_area_geografica_valuta_codice_idx; Type: INDEX; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE INDEX genrotit_area_geografica_valuta_codice_idx ON genrotit_area_geografica USING btree (valuta_codice);


--
-- Name: genrotit_banca_cap_idx; Type: INDEX; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE INDEX genrotit_banca_cap_idx ON genrotit_banca USING btree (cap);


--
-- Name: genrotit_banca_localita_idx; Type: INDEX; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE INDEX genrotit_banca_localita_idx ON genrotit_banca USING btree (localita);


--
-- Name: genrotit_emittente_area_geografica_id_idx; Type: INDEX; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE INDEX genrotit_emittente_area_geografica_id_idx ON genrotit_emittente USING btree (area_geografica_id);


--
-- Name: genrotit_gestione_banca_id_idx; Type: INDEX; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE INDEX genrotit_gestione_banca_id_idx ON genrotit_gestione USING btree (banca_id);


--
-- Name: genrotit_gestione_valuta_codice_idx; Type: INDEX; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE INDEX genrotit_gestione_valuta_codice_idx ON genrotit_gestione USING btree (valuta_codice);


--
-- Name: genrotit_h_tipo_titolo_code_idx; Type: INDEX; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE INDEX genrotit_h_tipo_titolo_code_idx ON genrotit_h_tipo_titolo USING btree (code);


--
-- Name: genrotit_h_tipo_titolo_parent_code_idx; Type: INDEX; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE INDEX genrotit_h_tipo_titolo_parent_code_idx ON genrotit_h_tipo_titolo USING btree (parent_code);


--
-- Name: genrotit_movimento_gestione_id_idx; Type: INDEX; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE INDEX genrotit_movimento_gestione_id_idx ON genrotit_movimento USING btree (gestione_id);


--
-- Name: genrotit_movimento_titolo_id_idx; Type: INDEX; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE INDEX genrotit_movimento_titolo_id_idx ON genrotit_movimento USING btree (titolo_id);


--
-- Name: genrotit_referente_banca_id_idx; Type: INDEX; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE INDEX genrotit_referente_banca_id_idx ON genrotit_referente USING btree (banca_id);


--
-- Name: genrotit_tipo_titolo_campo_campo_id_idx; Type: INDEX; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE INDEX genrotit_tipo_titolo_campo_campo_id_idx ON genrotit_tipo_titolo_campo USING btree (campo_id);


--
-- Name: genrotit_tipo_titolo_campo_tipo_titolo_id_idx; Type: INDEX; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE INDEX genrotit_tipo_titolo_campo_tipo_titolo_id_idx ON genrotit_tipo_titolo_campo USING btree (tipo_titolo_id);


--
-- Name: genrotit_titolo_area_geografica_id_idx; Type: INDEX; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE INDEX genrotit_titolo_area_geografica_id_idx ON genrotit_titolo USING btree (area_geografica_id);


--
-- Name: genrotit_titolo_emittente_id_idx; Type: INDEX; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE INDEX genrotit_titolo_emittente_id_idx ON genrotit_titolo USING btree (emittente_id);


--
-- Name: genrotit_titolo_h_tipo_titolo_id_idx; Type: INDEX; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE INDEX genrotit_titolo_h_tipo_titolo_id_idx ON genrotit_titolo USING btree (h_tipo_titolo_id);


--
-- Name: genrotit_titolo_valuta_codice_idx; Type: INDEX; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE INDEX genrotit_titolo_valuta_codice_idx ON genrotit_titolo USING btree (valuta_codice);


--
-- Name: genrotit_userobject_code_idx; Type: INDEX; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE INDEX genrotit_userobject_code_idx ON genrotit_userobject USING btree (code);


--
-- Name: genrotit_userobject_description_idx; Type: INDEX; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE INDEX genrotit_userobject_description_idx ON genrotit_userobject USING btree (description);


--
-- Name: genrotit_userobject_objtype_idx; Type: INDEX; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE INDEX genrotit_userobject_objtype_idx ON genrotit_userobject USING btree (objtype);


--
-- Name: genrotit_userobject_userid_idx; Type: INDEX; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE INDEX genrotit_userobject_userid_idx ON genrotit_userobject USING btree (userid);


--
-- Name: genrotit_valuta_storico_valuta_codice_idx; Type: INDEX; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE INDEX genrotit_valuta_storico_valuta_codice_idx ON genrotit_valuta_storico USING btree (valuta_codice);


--
-- Name: genrotit_valutazione_titolo_id_idx; Type: INDEX; Schema: genrotit; Owner: postgres; Tablespace: 
--

CREATE INDEX genrotit_valutazione_titolo_id_idx ON genrotit_valutazione USING btree (titolo_id);


SET search_path = glbl, pg_catalog;

--
-- Name: glbl_localita_cap_idx; Type: INDEX; Schema: glbl; Owner: postgres; Tablespace: 
--

CREATE INDEX glbl_localita_cap_idx ON glbl_localita USING btree (cap);


--
-- Name: glbl_localita_nome_idx; Type: INDEX; Schema: glbl; Owner: postgres; Tablespace: 
--

CREATE INDEX glbl_localita_nome_idx ON glbl_localita USING btree (nome);


--
-- Name: glbl_localita_provincia_idx; Type: INDEX; Schema: glbl; Owner: postgres; Tablespace: 
--

CREATE INDEX glbl_localita_provincia_idx ON glbl_localita USING btree (provincia);


--
-- Name: glbl_provincia_nome_idx; Type: INDEX; Schema: glbl; Owner: postgres; Tablespace: 
--

CREATE INDEX glbl_provincia_nome_idx ON glbl_provincia USING btree (nome);


--
-- Name: glbl_provincia_regione_idx; Type: INDEX; Schema: glbl; Owner: postgres; Tablespace: 
--

CREATE INDEX glbl_provincia_regione_idx ON glbl_provincia USING btree (regione);


--
-- Name: glbl_regione_nome_idx; Type: INDEX; Schema: glbl; Owner: postgres; Tablespace: 
--

CREATE INDEX glbl_regione_nome_idx ON glbl_regione USING btree (nome);


--
-- Name: glbl_stradario_cap_provincia_idx; Type: INDEX; Schema: glbl; Owner: postgres; Tablespace: 
--

CREATE INDEX glbl_stradario_cap_provincia_idx ON glbl_stradario_cap USING btree (provincia);


--
-- Name: glbl_userobject_code_idx; Type: INDEX; Schema: glbl; Owner: postgres; Tablespace: 
--

CREATE INDEX glbl_userobject_code_idx ON glbl_userobject USING btree (code);


--
-- Name: glbl_userobject_description_idx; Type: INDEX; Schema: glbl; Owner: postgres; Tablespace: 
--

CREATE INDEX glbl_userobject_description_idx ON glbl_userobject USING btree (description);


--
-- Name: glbl_userobject_objtype_idx; Type: INDEX; Schema: glbl; Owner: postgres; Tablespace: 
--

CREATE INDEX glbl_userobject_objtype_idx ON glbl_userobject USING btree (objtype);


--
-- Name: glbl_userobject_userid_idx; Type: INDEX; Schema: glbl; Owner: postgres; Tablespace: 
--

CREATE INDEX glbl_userobject_userid_idx ON glbl_userobject USING btree (userid);


SET search_path = sys, pg_catalog;

--
-- Name: sys_external_token_connection_id_idx; Type: INDEX; Schema: sys; Owner: postgres; Tablespace: 
--

CREATE INDEX sys_external_token_connection_id_idx ON sys_external_token USING btree (connection_id);


--
-- Name: sys_external_token_exec_user_idx; Type: INDEX; Schema: sys; Owner: postgres; Tablespace: 
--

CREATE INDEX sys_external_token_exec_user_idx ON sys_external_token USING btree (exec_user);


--
-- Name: sys_external_token_use_external_token_id_idx; Type: INDEX; Schema: sys; Owner: postgres; Tablespace: 
--

CREATE INDEX sys_external_token_use_external_token_id_idx ON sys_external_token_use USING btree (external_token_id);


--
-- Name: sys_locked_record_lock_table_lock_pkey_idx; Type: INDEX; Schema: sys; Owner: postgres; Tablespace: 
--

CREATE UNIQUE INDEX sys_locked_record_lock_table_lock_pkey_idx ON sys_locked_record USING btree (lock_table, lock_pkey);


--
-- Name: sys_message_dst_connection_id_idx; Type: INDEX; Schema: sys; Owner: postgres; Tablespace: 
--

CREATE INDEX sys_message_dst_connection_id_idx ON sys_message USING btree (dst_connection_id);


--
-- Name: sys_message_dst_page_id_idx; Type: INDEX; Schema: sys; Owner: postgres; Tablespace: 
--

CREATE INDEX sys_message_dst_page_id_idx ON sys_message USING btree (dst_page_id);


--
-- Name: sys_message_dst_user_idx; Type: INDEX; Schema: sys; Owner: postgres; Tablespace: 
--

CREATE INDEX sys_message_dst_user_idx ON sys_message USING btree (dst_user);


--
-- Name: sys_message_src_connection_id_idx; Type: INDEX; Schema: sys; Owner: postgres; Tablespace: 
--

CREATE INDEX sys_message_src_connection_id_idx ON sys_message USING btree (src_connection_id);


--
-- Name: sys_message_src_page_id_idx; Type: INDEX; Schema: sys; Owner: postgres; Tablespace: 
--

CREATE INDEX sys_message_src_page_id_idx ON sys_message USING btree (src_page_id);


--
-- Name: sys_message_src_user_idx; Type: INDEX; Schema: sys; Owner: postgres; Tablespace: 
--

CREATE INDEX sys_message_src_user_idx ON sys_message USING btree (src_user);


--
-- Name: sys_userobject_code_idx; Type: INDEX; Schema: sys; Owner: postgres; Tablespace: 
--

CREATE INDEX sys_userobject_code_idx ON sys_userobject USING btree (code);


--
-- Name: sys_userobject_description_idx; Type: INDEX; Schema: sys; Owner: postgres; Tablespace: 
--

CREATE INDEX sys_userobject_description_idx ON sys_userobject USING btree (description);


--
-- Name: sys_userobject_objtype_idx; Type: INDEX; Schema: sys; Owner: postgres; Tablespace: 
--

CREATE INDEX sys_userobject_objtype_idx ON sys_userobject USING btree (objtype);


--
-- Name: sys_userobject_userid_idx; Type: INDEX; Schema: sys; Owner: postgres; Tablespace: 
--

CREATE INDEX sys_userobject_userid_idx ON sys_userobject USING btree (userid);


SET search_path = test15, pg_catalog;

--
-- Name: test15_recursive_parent_id_idx; Type: INDEX; Schema: test15; Owner: postgres; Tablespace: 
--

CREATE INDEX test15_recursive_parent_id_idx ON test15_recursive USING btree (parent_id);


--
-- Name: test15_userobject_code_idx; Type: INDEX; Schema: test15; Owner: postgres; Tablespace: 
--

CREATE INDEX test15_userobject_code_idx ON test15_userobject USING btree (code);


--
-- Name: test15_userobject_description_idx; Type: INDEX; Schema: test15; Owner: postgres; Tablespace: 
--

CREATE INDEX test15_userobject_description_idx ON test15_userobject USING btree (description);


--
-- Name: test15_userobject_objtype_idx; Type: INDEX; Schema: test15; Owner: postgres; Tablespace: 
--

CREATE INDEX test15_userobject_objtype_idx ON test15_userobject USING btree (objtype);


--
-- Name: test15_userobject_userid_idx; Type: INDEX; Schema: test15; Owner: postgres; Tablespace: 
--

CREATE INDEX test15_userobject_userid_idx ON test15_userobject USING btree (userid);


SET search_path = adm, pg_catalog;

--
-- Name: fk_adm_authorization_user_id; Type: FK CONSTRAINT; Schema: adm; Owner: postgres
--

ALTER TABLE ONLY adm_authorization
    ADD CONSTRAINT fk_adm_authorization_user_id FOREIGN KEY (user_id) REFERENCES adm_user(id);


--
-- Name: fk_adm_permission_datacatalog_id; Type: FK CONSTRAINT; Schema: adm; Owner: postgres
--

ALTER TABLE ONLY adm_permission
    ADD CONSTRAINT fk_adm_permission_datacatalog_id FOREIGN KEY (datacatalog_id) REFERENCES adm_datacatalog(id);


--
-- Name: fk_adm_permission_tag_id; Type: FK CONSTRAINT; Schema: adm; Owner: postgres
--

ALTER TABLE ONLY adm_permission
    ADD CONSTRAINT fk_adm_permission_tag_id FOREIGN KEY (tag_id) REFERENCES adm_htag(id);


--
-- Name: fk_adm_served_page_connection_id; Type: FK CONSTRAINT; Schema: adm; Owner: postgres
--

ALTER TABLE ONLY adm_served_page
    ADD CONSTRAINT fk_adm_served_page_connection_id FOREIGN KEY (connection_id) REFERENCES adm_connection(id);


--
-- Name: fk_adm_user_tag_tag_id; Type: FK CONSTRAINT; Schema: adm; Owner: postgres
--

ALTER TABLE ONLY adm_user_tag
    ADD CONSTRAINT fk_adm_user_tag_tag_id FOREIGN KEY (tag_id) REFERENCES adm_htag(id);


--
-- Name: fk_adm_user_tag_user_id; Type: FK CONSTRAINT; Schema: adm; Owner: postgres
--

ALTER TABLE ONLY adm_user_tag
    ADD CONSTRAINT fk_adm_user_tag_user_id FOREIGN KEY (user_id) REFERENCES adm_user(id);


SET search_path = genrotit, pg_catalog;

--
-- Name: fk_genrotit_area_geografica_valuta_codice; Type: FK CONSTRAINT; Schema: genrotit; Owner: postgres
--

ALTER TABLE ONLY genrotit_area_geografica
    ADD CONSTRAINT fk_genrotit_area_geografica_valuta_codice FOREIGN KEY (valuta_codice) REFERENCES genrotit_valuta(codice);


--
-- Name: fk_genrotit_emittente_area_geografica_id; Type: FK CONSTRAINT; Schema: genrotit; Owner: postgres
--

ALTER TABLE ONLY genrotit_emittente
    ADD CONSTRAINT fk_genrotit_emittente_area_geografica_id FOREIGN KEY (area_geografica_id) REFERENCES genrotit_area_geografica(id);


--
-- Name: fk_genrotit_gestione_banca_id; Type: FK CONSTRAINT; Schema: genrotit; Owner: postgres
--

ALTER TABLE ONLY genrotit_gestione
    ADD CONSTRAINT fk_genrotit_gestione_banca_id FOREIGN KEY (banca_id) REFERENCES genrotit_banca(id);


--
-- Name: fk_genrotit_gestione_valuta_codice; Type: FK CONSTRAINT; Schema: genrotit; Owner: postgres
--

ALTER TABLE ONLY genrotit_gestione
    ADD CONSTRAINT fk_genrotit_gestione_valuta_codice FOREIGN KEY (valuta_codice) REFERENCES genrotit_valuta(codice);


--
-- Name: fk_genrotit_movimento_gestione_id; Type: FK CONSTRAINT; Schema: genrotit; Owner: postgres
--

ALTER TABLE ONLY genrotit_movimento
    ADD CONSTRAINT fk_genrotit_movimento_gestione_id FOREIGN KEY (gestione_id) REFERENCES genrotit_gestione(id);


--
-- Name: fk_genrotit_movimento_titolo_id; Type: FK CONSTRAINT; Schema: genrotit; Owner: postgres
--

ALTER TABLE ONLY genrotit_movimento
    ADD CONSTRAINT fk_genrotit_movimento_titolo_id FOREIGN KEY (titolo_id) REFERENCES genrotit_titolo(id);


--
-- Name: fk_genrotit_referente_banca_id; Type: FK CONSTRAINT; Schema: genrotit; Owner: postgres
--

ALTER TABLE ONLY genrotit_referente
    ADD CONSTRAINT fk_genrotit_referente_banca_id FOREIGN KEY (banca_id) REFERENCES genrotit_banca(id);


--
-- Name: fk_genrotit_tipo_titolo_campo_campo_id; Type: FK CONSTRAINT; Schema: genrotit; Owner: postgres
--

ALTER TABLE ONLY genrotit_tipo_titolo_campo
    ADD CONSTRAINT fk_genrotit_tipo_titolo_campo_campo_id FOREIGN KEY (campo_id) REFERENCES genrotit_campo(id);


--
-- Name: fk_genrotit_tipo_titolo_campo_tipo_titolo_id; Type: FK CONSTRAINT; Schema: genrotit; Owner: postgres
--

ALTER TABLE ONLY genrotit_tipo_titolo_campo
    ADD CONSTRAINT fk_genrotit_tipo_titolo_campo_tipo_titolo_id FOREIGN KEY (tipo_titolo_id) REFERENCES genrotit_h_tipo_titolo(id);


--
-- Name: fk_genrotit_titolo_area_geografica_id; Type: FK CONSTRAINT; Schema: genrotit; Owner: postgres
--

ALTER TABLE ONLY genrotit_titolo
    ADD CONSTRAINT fk_genrotit_titolo_area_geografica_id FOREIGN KEY (area_geografica_id) REFERENCES genrotit_area_geografica(id);


--
-- Name: fk_genrotit_titolo_emittente_id; Type: FK CONSTRAINT; Schema: genrotit; Owner: postgres
--

ALTER TABLE ONLY genrotit_titolo
    ADD CONSTRAINT fk_genrotit_titolo_emittente_id FOREIGN KEY (emittente_id) REFERENCES genrotit_emittente(id);


--
-- Name: fk_genrotit_titolo_h_tipo_titolo_id; Type: FK CONSTRAINT; Schema: genrotit; Owner: postgres
--

ALTER TABLE ONLY genrotit_titolo
    ADD CONSTRAINT fk_genrotit_titolo_h_tipo_titolo_id FOREIGN KEY (h_tipo_titolo_id) REFERENCES genrotit_h_tipo_titolo(id);


--
-- Name: fk_genrotit_titolo_valuta_codice; Type: FK CONSTRAINT; Schema: genrotit; Owner: postgres
--

ALTER TABLE ONLY genrotit_titolo
    ADD CONSTRAINT fk_genrotit_titolo_valuta_codice FOREIGN KEY (valuta_codice) REFERENCES genrotit_valuta(codice);


--
-- Name: fk_genrotit_valuta_storico_valuta_codice; Type: FK CONSTRAINT; Schema: genrotit; Owner: postgres
--

ALTER TABLE ONLY genrotit_valuta_storico
    ADD CONSTRAINT fk_genrotit_valuta_storico_valuta_codice FOREIGN KEY (valuta_codice) REFERENCES genrotit_valuta(codice);


--
-- Name: fk_genrotit_valutazione_titolo_id; Type: FK CONSTRAINT; Schema: genrotit; Owner: postgres
--

ALTER TABLE ONLY genrotit_valutazione
    ADD CONSTRAINT fk_genrotit_valutazione_titolo_id FOREIGN KEY (titolo_id) REFERENCES genrotit_titolo(id);


SET search_path = glbl, pg_catalog;

--
-- Name: fk_glbl_localita_provincia; Type: FK CONSTRAINT; Schema: glbl; Owner: postgres
--

ALTER TABLE ONLY glbl_localita
    ADD CONSTRAINT fk_glbl_localita_provincia FOREIGN KEY (provincia) REFERENCES glbl_provincia(sigla) ON UPDATE CASCADE;


SET search_path = sys, pg_catalog;

--
-- Name: fk_sys_external_token_use_external_token_id; Type: FK CONSTRAINT; Schema: sys; Owner: postgres
--

ALTER TABLE ONLY sys_external_token_use
    ADD CONSTRAINT fk_sys_external_token_use_external_token_id FOREIGN KEY (external_token_id) REFERENCES sys_external_token(id);


SET search_path = test15, pg_catalog;

--
-- Name: fk_test15_recursive_parent_id; Type: FK CONSTRAINT; Schema: test15; Owner: postgres
--

ALTER TABLE ONLY test15_recursive
    ADD CONSTRAINT fk_test15_recursive_parent_id FOREIGN KEY (parent_id) REFERENCES test15_recursive(id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

