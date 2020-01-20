CREATE TABLE guild_settings(
    guild_id BIGINT PRIMARY KEY,
    prefix VARCHAR(30)
);


CREATE TABLE command_names(
    guild_id BIGINT,
    command_name VARCHAR(30),
    enabled BOOLEAN DEFAULT TRUE,
    nsfw BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (guild_id, command_name)
);


CREATE TABLE command_responses(
    guild_id BIGINT,
    command_name VARCHAR(30),
    response VARCHAR(2000),
    PRIMARY KEY (guild_id, command_name, response)
);
