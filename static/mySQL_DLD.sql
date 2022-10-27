CREATE TABLE accounts (
  id int NOT NULL AUTO_INCREMENT,
  phone varchar(15) NOT NULL,
  username varchar(20) NOT NULL,
  email varchar(100) NOT NULL,
  password varchar(255) NOT NULL,
  team int NOT NULL DEFAULT '0',
  PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8

CREATE TABLE memos (
  id int NOT NULL AUTO_INCREMENT,
  ad varchar(45) NOT NULL,
  username varchar(20) NOT NULL,
  memo varchar(1001) NOT NULL,
  pubdate varchar(45) NOT NULL,
  team int NOT NULL DEFAULT '0',
  PRIMARY KEY (id)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8

CREATE TABLE timeline (
  idnew_table int NOT NULL AUTO_INCREMENT,
  username varchar(45) NOT NULL,
  date date NOT NULL,
  title varchar(500) NOT NULL,
  team int NOT NULL DEFAULT '0',
  PRIMARY KEY (idnew_table)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb3
