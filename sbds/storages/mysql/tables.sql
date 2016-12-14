drop database steem;
create database steem;
use steem;
CREATE TABLE IF NOT EXISTS Accounts (
	id varchar(15) NOT NULL,
	name varchar(50) NOT NULL,
	owner LONGTEXT NOT NULL,
	active LONGTEXT NOT NULL,
	posting LONGTEXT NOT NULL,
	memo_key LONGTEXT NOT NULL,
	json_metadata LONGTEXT,
	proxy varchar(50),
	last_owner_update datetime NOT NULL,
	last_account_update datetime NOT NULL,
	created datetime NOT NULL,
	mined smallint NOT NULL,
	owner_challenged smallint NOT NULL,
	active_challenged smallint NOT NULL,
	last_owner_proved datetime NOT NULL,
	last_active_proved datetime NOT NULL,
	recovery_account varchar(50) NOT NULL,
	last_account_recovery datetime NOT NULL,
	reset_account varchar(50) NOT NULL,
	comment_count bigint NOT NULL,
	lifetime_vote_count bigint NOT NULL,
	post_count bigint NOT NULL,
	can_vote smallint NOT NULL,
	voting_power smallint NOT NULL,
	last_vote_time datetime NOT NULL,
	balance varchar(50) NOT NULL,
	savings_balance varchar(50) NOT NULL,
	sbd_balance varchar(50) NOT NULL,
	sbd_seconds bigint NOT NULL,
	sbd_seconds_last_update datetime NOT NULL,
	sbd_last_interest_payment datetime NOT NULL,
	savings_sbd_balance varchar(50) NOT NULL,
	savings_sbd_seconds bigint NOT NULL,
	savings_sbd_seconds_last_update datetime NOT NULL,
	savings_sbd_last_interest_payment datetime NOT NULL,
	savings_withdraw_requests integer NOT NULL,
	vesting_shares varchar(50) NOT NULL,
	vesting_withdraw_rate varchar(50) NOT NULL,
	next_vesting_withdrawal datetime NOT NULL,
	withdrawn bigint NOT NULL,
	to_withdraw bigint NOT NULL,
	withdraw_routes smallint NOT NULL,
	curation_rewards bigint NOT NULL,
	posting_rewards bigint NOT NULL,
	proxied_vsf_votes LONGTEXT NOT NULL,
	witnesses_voted_for smallint NOT NULL,
	average_bandwidth bigint NOT NULL,
	lifetime_bandwidth bigint NOT NULL,
	last_bandwidth_update datetime NOT NULL,
	average_market_bandwidth bigint NOT NULL,
	last_market_bandwidth_update datetime NOT NULL,
	last_post datetime NOT NULL,
	last_root_post datetime NOT NULL,
	post_bandwidth bigint NOT NULL,
	vesting_balance varchar(50) NOT NULL,
	reputation varchar(50) NOT NULL,
	transfer_history LONGTEXT,
	market_history LONGTEXT,
	post_history LONGTEXT,
	vote_history LONGTEXT,
	other_history LONGTEXT,
	witness_votes LONGTEXT,
	blog_category LONGTEXT,
	dirty smallint NOT NULL,
	PRIMARY KEY (name)
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE IF NOT EXISTS Blocks (
	raw JSON NOT NULL,
	block_num INT GENERATED ALWAYS AS (CONV(LEFT(raw->>"$.previous", 8), 16, 10) + 1) STORED PRIMARY KEY,
	previous varchar(50) GENERATED ALWAYS AS (raw->>"$.previous") STORED NOT NULL,
	timestamp datetime GENERATED ALWAYS AS (raw->>"$.timestamp") STORED NOT NULL,
	witness varchar(50) GENERATED ALWAYS AS (raw->>"$.witness") STORED NOT NULL,
	witness_signature varchar(150) GENERATED ALWAYS AS (raw->>"$.witness_signature") STORED NOT NULL,
	transaction_merkle_root varchar(50) GENERATED ALWAYS AS (raw->>"$.transaction_merkle_root") STORED NOT NULL,
	extensions JSON GENERATED ALWAYS AS (raw->>"$.extentions") STORED,
	transactions JSON GENERATED ALWAYS AS (raw->>"$.transactions") STORED
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE IF NOT EXISTS Comments (
	ID integer NOT NULL auto_increment,
	author varchar(50) NOT NULL,
	permlink varchar(512) NOT NULL,
	category LONGTEXT NOT NULL,
	last_update datetime NOT NULL,
	created datetime NOT NULL,
	active datetime NOT NULL,
	last_payout datetime NOT NULL,
	depth integer NOT NULL,
	children integer NOT NULL,
	children_rshares2 float(53) NOT NULL,
	net_rshares bigint NOT NULL,
	abs_rshares bigint NOT NULL,
	vote_rshares bigint NOT NULL,
	children_abs_rshares bigint NOT NULL,
	cashout_time datetime NOT NULL,
	max_cashout_time datetime NOT NULL,
	total_vote_weight float(53) NOT NULL,
	reward_weight integer NOT NULL,
	total_payout_value decimal(19,4) NOT NULL,
	curator_payout_value decimal(19,4) NOT NULL,
	author_rewards decimal(19,4) NOT NULL,
	net_votes integer NOT NULL,
	root_comment varchar(50) NOT NULL,
	mode varchar(50) NOT NULL,
	max_accepted_payout decimal(19,4) NOT NULL,
	percent_steem_dollars integer NOT NULL,
	allow_replies smallint NOT NULL,
	allow_votes smallint NOT NULL,
	allow_curation_rewards smallint NOT NULL,
	url LONGTEXT NOT NULL,
	root_title LONGTEXT NOT NULL,
	pending_payout_value decimal(19,4) NOT NULL,
	total_pending_payout_value decimal(19,4) NOT NULL,
	active_votes LONGTEXT NOT NULL,
	replies LONGTEXT NOT NULL,
	author_reputation bigint NOT NULL,
	body_language varchar(512),
	PRIMARY KEY (ID)
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE IF NOT EXISTS Transactions (
	tx_id integer NOT NULL auto_increment,
	block_num integer NOT NULL,
	transaction_num smallint NOT NULL,
	ref_block_num integer NOT NULL,
	ref_block_prefix bigint NOT NULL,
	expiration datetime NOT NULL,
	type varchar(50) NOT NULL,
	PRIMARY KEY (tx_id)
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE IF NOT EXISTS TxAccountCreates (
	ID integer NOT NULL auto_increment,
	tx_id integer NOT NULL,
	fee decimal(19,4) NOT NULL,
	creator varchar(50) NOT NULL,
	new_account_name varchar(50),
	owner_key varchar(80) NOT NULL,
	active_key varchar(80) NOT NULL,
	posting_key varchar(80) NOT NULL,
	memo_key LONGTEXT NOT NULL,
	json_metadata LONGTEXT NOT NULL,
	PRIMARY KEY (ID)
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE IF NOT EXISTS TxAccountRecovers (
	ID integer NOT NULL auto_increment,
	tx_id integer NOT NULL,
	recovery_account varchar(50),
	account_to_recover varchar(50) NOT NULL,
	recovered smallint NOT NULL,
	PRIMARY KEY (ID)
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE IF NOT EXISTS TxAccountUpdates (
	ID integer NOT NULL auto_increment,
	tx_id integer NOT NULL,
	account varchar(50),
	key_auth1 varchar(80),
	key_auth2 varchar(80),
	memo_key LONGTEXT NOT NULL,
	json_metadata LONGTEXT NOT NULL,
	PRIMARY KEY (ID)
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE IF NOT EXISTS TxAccountWitnessProxies (
	ID integer NOT NULL auto_increment,
	tx_id integer NOT NULL,
	account varchar(50) NOT NULL,
	Proxy varchar(50) NOT NULL,
	PRIMARY KEY (ID)
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE IF NOT EXISTS TxAccountWitnessVotes (
	ID integer NOT NULL auto_increment,
	tx_id integer NOT NULL,
	account varchar(50) NOT NULL,
	witness varchar(50) NOT NULL,
	approve smallint NOT NULL,
	PRIMARY KEY (ID)
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE IF NOT EXISTS TxAuthorRewards (
	ID integer NOT NULL auto_increment,
	tx_id integer NOT NULL,
	author varchar(50) NOT NULL,
	permlink varchar(512) NOT NULL,
	sdb_payout decimal(19,4) NOT NULL,
	steem_payout decimal(19,4) NOT NULL,
	vesting_payout decimal(19,4) NOT NULL,
	PRIMARY KEY (ID)
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE IF NOT EXISTS TxComments (
	ID integer NOT NULL auto_increment,
	tx_id integer NOT NULL,
	author varchar(50) NOT NULL,
	permlink varchar(512) NOT NULL,
	parent_author varchar(50) NOT NULL,
	parent_permlink varchar(512) NOT NULL,
	title LONGTEXT NOT NULL,
	body LONGTEXT NOT NULL,
	json_metadata LONGTEXT NOT NULL,
	PRIMARY KEY (ID)
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE IF NOT EXISTS TxCommentsOptions (
	ID integer NOT NULL auto_increment,
	tx_id integer NOT NULL,
	author varchar(50) NOT NULL,
	permlink varchar(512) NOT NULL,
	max_accepted_payout decimal(19,4) NOT NULL,
	percent_steem_dollars smallint NOT NULL,
	allow_votes smallint NOT NULL,
	allow_curation_rewards smallint NOT NULL,
	PRIMARY KEY (ID)
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE IF NOT EXISTS TxConverts (
	ID integer NOT NULL auto_increment,
	tx_id integer NOT NULL,
	owner varchar(50) NOT NULL,
	requestid bigint NOT NULL,
	amount decimal(19,4) NOT NULL,
	PRIMARY KEY (ID)
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE IF NOT EXISTS TxCurationRewards (
	ID integer NOT NULL auto_increment,
	tx_id integer NOT NULL,
	curator varchar(50) NOT NULL,
	comment_author varchar(50) NOT NULL,
	comment_permlink varchar(512) NOT NULL,
	reward varchar(50) NOT NULL,
	PRIMARY KEY (ID)
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE IF NOT EXISTS TxCustoms (
	ID integer NOT NULL auto_increment,
	tx_id integer NOT NULL,
	tid varchar(50) NOT NULL,
	json_metadata LONGTEXT NOT NULL,
	PRIMARY KEY (ID)
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE IF NOT EXISTS TxDeleteComments (
	ID integer NOT NULL auto_increment,
	tx_id integer NOT NULL,
	author varchar(50) NOT NULL,
	permlink LONGTEXT NOT NULL,
	PRIMARY KEY (ID)
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE IF NOT EXISTS TxFeeds (
	ID integer NOT NULL auto_increment,
	tx_id integer NOT NULL,
	publisher varchar(50) NOT NULL,
	exchange_rate_base decimal(19,4) NOT NULL,
	exchange_rate_quote decimal(19,4) NOT NULL,
	PRIMARY KEY (ID)
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE IF NOT EXISTS TxLimitOrders (
	ID integer NOT NULL auto_increment,
	tx_id integer NOT NULL,
	owner varchar(50) NOT NULL,
	orderid bigint NOT NULL,
	cancel smallint NOT NULL,
	amount_to_sell decimal(19,4),
	min_to_receive decimal(19,4),
	fill_or_kill smallint NOT NULL,
	expiration datetime,
	PRIMARY KEY (ID)
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE IF NOT EXISTS TxPows (
	ID integer NOT NULL auto_increment,
	tx_id integer NOT NULL,
	worker_account varchar(50) NOT NULL,
	block_id varchar(40) NOT NULL,
	PRIMARY KEY (ID)
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE IF NOT EXISTS TxTransfers (
	ID integer NOT NULL auto_increment,
	tx_id integer NOT NULL,
	type varchar(50) NOT NULL,
	`from` varchar(50) NOT NULL,
	`to` varchar(50) NOT NULL,
	amount decimal(19,4) NOT NULL,
	amount_symbol varchar(5),
	memo LONGTEXT,
	request_id integer NOT NULL,
	PRIMARY KEY (ID)
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE IF NOT EXISTS TxVotes (
	ID integer NOT NULL auto_increment,
	tx_id integer NOT NULL,
	voter varchar(50) NOT NULL,
	author varchar(50) NOT NULL,
	permlink varchar(512) NOT NULL,
	weight integer NOT NULL,
	PRIMARY KEY (ID)
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE IF NOT EXISTS TxWithdrawVestingRoutes (
	ID integer NOT NULL auto_increment,
	tx_id integer NOT NULL,
	from_account varchar(50) NOT NULL,
	to_account varchar(50) NOT NULL,
	percent smallint NOT NULL,
	auto_vest smallint NOT NULL,
	PRIMARY KEY (ID)
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE IF NOT EXISTS TxWithdraws (
	ID integer NOT NULL auto_increment,
	tx_id integer NOT NULL,
	account varchar(50) NOT NULL,
	vesting_shares decimal(19,4) NOT NULL,
	PRIMARY KEY (ID)
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
CREATE TABLE IF NOT EXISTS TxWitnessUpdates (
	ID integer NOT NULL auto_increment,
	tx_id integer NOT NULL,
	owner varchar(50) NOT NULL,
	url LONGTEXT NOT NULL,
	block_signing_key varchar(64) NOT NULL,
	props_account_creation_fee decimal(19,4) NOT NULL,
	props_maximum_block_size integer NOT NULL,
	props_sbd_interest_rate integer NOT NULL,
	fee decimal(19,4) NOT NULL,
	PRIMARY KEY (ID)
) ENGINE InnoDB DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;
ALTER TABLE Transactions
	ADD FOREIGN KEY (block_num) 
	REFERENCES Blocks (block_num);


ALTER TABLE TxAccountCreates
	ADD FOREIGN KEY (tx_id) 
	REFERENCES Transactions (tx_id);


ALTER TABLE TxAccountRecovers
	ADD FOREIGN KEY (tx_id) 
	REFERENCES Transactions (tx_id);


ALTER TABLE TxAccountUpdates
	ADD FOREIGN KEY (tx_id) 
	REFERENCES Transactions (tx_id);


ALTER TABLE TxAccountWitnessProxies
	ADD FOREIGN KEY (tx_id) 
	REFERENCES Transactions (tx_id);


ALTER TABLE TxAccountWitnessVotes
	ADD FOREIGN KEY (tx_id) 
	REFERENCES Transactions (tx_id);


ALTER TABLE TxAuthorRewards
	ADD FOREIGN KEY (tx_id) 
	REFERENCES Transactions (tx_id);


ALTER TABLE TxCommentsOptions
	ADD FOREIGN KEY (tx_id) 
	REFERENCES Transactions (tx_id);


ALTER TABLE TxConverts
	ADD FOREIGN KEY (tx_id) 
	REFERENCES Transactions (tx_id);


ALTER TABLE TxCurationRewards
	ADD FOREIGN KEY (tx_id) 
	REFERENCES Transactions (tx_id);


ALTER TABLE TxCustoms
	ADD FOREIGN KEY (tx_id) 
	REFERENCES Transactions (tx_id);


ALTER TABLE TxDeleteComments
	ADD FOREIGN KEY (tx_id) 
	REFERENCES Transactions (tx_id);


ALTER TABLE TxFeeds
	ADD FOREIGN KEY (tx_id) 
	REFERENCES Transactions (tx_id);


ALTER TABLE TxLimitOrders
	ADD FOREIGN KEY (tx_id) 
	REFERENCES Transactions (tx_id);


ALTER TABLE TxPows
	ADD FOREIGN KEY (tx_id) 
	REFERENCES Transactions (tx_id);


ALTER TABLE TxTransfers
	ADD FOREIGN KEY (tx_id) 
	REFERENCES Transactions (tx_id);


ALTER TABLE TxVotes
	ADD FOREIGN KEY (tx_id) 
	REFERENCES Transactions (tx_id);


ALTER TABLE TxWithdrawVestingRoutes
	ADD FOREIGN KEY (tx_id) 
	REFERENCES Transactions (tx_id);


ALTER TABLE TxWithdraws
	ADD FOREIGN KEY (tx_id) 
	REFERENCES Transactions (tx_id);


ALTER TABLE TxWitnessUpdates
	ADD FOREIGN KEY (tx_id) 
	REFERENCES Transactions (tx_id);