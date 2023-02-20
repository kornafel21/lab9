CREATE TABLE users(
   id SERIAL NOT NULL PRIMARY KEY,
   username VARCHAR (50) NOT NULL,
   password VARCHAR (255) NOT NULL,
   phone VARCHAR(100) NOT NULL,
   first_name VARCHAR (50) NOT NULL,
   last_name VARCHAR (20) NOT NULL,
   email VARCHAR(100) NOT NULL,
   user_status INT NOT NULL,
   CONSTRAINT unique_username UNIQUE(username)
);


CREATE TABLE article(
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    text VARCHAR(2000) NOT NULL,
    version INT NOT NULL,
    creator_id INT NOT NULL,
    CONSTRAINT fk_creatorId FOREIGN KEY (creator_id) REFERENCES users (id)
);


CREATE TABLE change(
    id SERIAL PRIMARY KEY,
    article_id INT NOT NULL,
    article_version INT NOT NULL,
    old_text VARCHAR(2000) NOT NULL,
    new_text VARCHAR(2000) NOT NULL,
    status VARCHAR(9) NOT NULL,
    proposer_id INT NOT NULL,
    CONSTRAINT fk_articleId FOREIGN KEY (article_id) REFERENCES article (id),
    CONSTRAINT fk_proposerId FOREIGN KEY (proposer_id) REFERENCES users (id)
);


CREATE TABLE review(
    id SERIAL PRIMARY KEY,
    change_id INT NOT NULL,
    verdict BOOLEAN NOT NULL,
    comment VARCHAR(200) NOT NULL,
    reviewer_id INT NOT NULL,
    CONSTRAINT unique_changeId UNIQUE(change_id),
    CONSTRAINT fk_changeId FOREIGN KEY (change_id) REFERENCES change (id),
    CONSTRAINT fk_reviewerId FOREIGN KEY (reviewer_id) REFERENCES users (id)
);






