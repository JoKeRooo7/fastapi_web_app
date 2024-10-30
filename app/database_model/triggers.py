from sqlalchemy import text


async def setup_user_accounts_triggers(engine):
    async with engine.begin() as conn:
        await conn.execute(text("""
            DROP TRIGGER IF EXISTS log_user_accounts_insert;
        """))
        await conn.execute(text("""
            DROP TRIGGER IF EXISTS log_user_accounts_update;
        """))
        await conn.execute(text("""
            DROP TRIGGER IF EXISTS log_user_accounts_delete;
        """))
        await conn.execute(text("""
            CREATE TRIGGER log_user_accounts_insert
            AFTER INSERT ON user_accounts
            BEGIN
                INSERT INTO user_accounts_log (user_id, action, changed_column, new_value, action_timestamp)
                VALUES (NEW.id, 'INSERT', 'all_columns', json_object('id', NEW.id, 'username', NEW.username, 'hashed_password', NEW.hashed_password), CURRENT_TIMESTAMP);
            END;
        """))
        await conn.execute(text("""
            CREATE TRIGGER log_user_accounts_update
            AFTER UPDATE ON user_accounts
            FOR EACH ROW
            BEGIN
                -- Логирование изменений для username
                INSERT INTO user_accounts_log (user_id, action, changed_column, old_value, new_value, action_timestamp)
                VALUES (OLD.id, 'UPDATE', 'username', OLD.username, NEW.username, CURRENT_TIMESTAMP);

                -- Логирование изменений для hashed_password
                INSERT INTO user_accounts_log (user_id, action, changed_column, old_value, new_value, action_timestamp)
                VALUES (OLD.id, 'UPDATE', 'hashed_password', OLD.hashed_password, NEW.hashed_password, CURRENT_TIMESTAMP);
            END;
        """))
        await conn.execute(text("""
            CREATE TRIGGER log_user_accounts_delete
            AFTER DELETE ON user_accounts
            BEGIN
                INSERT INTO user_accounts_log (user_id, action, changed_column, old_value, action_timestamp)
                VALUES (OLD.id, 'DELETE', 'all_columns', json_object('id', OLD.id, 'username', OLD.username, 'hashed_password', OLD.hashed_password), CURRENT_TIMESTAMP);
            END;
        """))

async def setup_user_mails_triggers(engine):
    async with engine.begin() as conn:
        await conn.execute(text("""
            DROP TRIGGER IF EXISTS log_user_mails_insert;
        """))
        await conn.execute(text("""
            DROP TRIGGER IF EXISTS log_user_mails_update;
        """))
        await conn.execute(text("""
            DROP TRIGGER IF EXISTS log_user_mails_delete;
        """))
        await conn.execute(text("""
            CREATE TRIGGER log_user_mails_insert
            AFTER INSERT ON user_mails
            BEGIN
                INSERT INTO user_mails_log (user_id, action, changed_column, new_value, action_timestamp)
                VALUES (NEW.user_id, 'INSERT', 'all_columns', json_object('id', NEW.id, 'email', NEW.email, 'gender', NEW.gender), CURRENT_TIMESTAMP);
            END;
        """))
        await conn.execute(text("""
            CREATE TRIGGER log_user_mails_update
            AFTER UPDATE ON user_mails
            FOR EACH ROW
            BEGIN
                -- Логирование изменений для email
                INSERT INTO user_mails_log (user_id, action, changed_column, old_value, new_value, action_timestamp)
                VALUES (OLD.user_id, 'UPDATE', 'email', OLD.email, NEW.email, CURRENT_TIMESTAMP);

                -- Логирование изменений для gender
                INSERT INTO user_mails_log (user_id, action, changed_column, old_value, new_value, action_timestamp)
                VALUES (OLD.user_id, 'UPDATE', 'gender', OLD.gender, NEW.gender, CURRENT_TIMESTAMP);
            END;
        """))
        await conn.execute(text("""
            CREATE TRIGGER log_user_mails_delete
            AFTER DELETE ON user_mails
            BEGIN
                INSERT INTO user_mails_log (user_id, action, changed_column, old_value, action_timestamp)
                VALUES (OLD.user_id, 'DELETE', 'all_columns', json_object('id', OLD.id, 'email', OLD.email, 'gender', OLD.gender), CURRENT_TIMESTAMP);
            END;
        """))

async def setup_user_names_triggers(engine):
    async with engine.begin() as conn:
        await conn.execute(text("""
            DROP TRIGGER IF EXISTS log_user_names_insert;
        """))
        await conn.execute(text("""
            DROP TRIGGER IF EXISTS log_user_names_update;
        """))
        await conn.execute(text("""
            DROP TRIGGER IF EXISTS log_user_names_delete;
        """))
        await conn.execute(text("""
            CREATE TRIGGER log_user_names_insert
            AFTER INSERT ON user_names
            BEGIN
                INSERT INTO user_names_log (user_id, action, changed_column, new_value, action_timestamp)
                VALUES (NEW.user_id, 'INSERT', 'all_columns', json_object('first_name', NEW.first_name, 'last_name', NEW.last_name), CURRENT_TIMESTAMP);
            END;
        """))
        await conn.execute(text("""
            CREATE TRIGGER log_user_names_update
            AFTER UPDATE ON user_names
            FOR EACH ROW
            BEGIN
                -- Логирование изменений для first_name
                INSERT INTO user_names_log (user_id, action, changed_column, old_value, new_value, action_timestamp)
                VALUES (OLD.user_id, 'UPDATE', 'first_name', OLD.first_name, NEW.first_name, CURRENT_TIMESTAMP);

                -- Логирование изменений для last_name
                INSERT INTO user_names_log (user_id, action, changed_column, old_value, new_value, action_timestamp)
                VALUES (OLD.user_id, 'UPDATE', 'last_name', OLD.last_name, NEW.last_name, CURRENT_TIMESTAMP);
            END;
        """))
        await conn.execute(text("""
            CREATE TRIGGER log_user_names_delete
            AFTER DELETE ON user_names
            BEGIN
                INSERT INTO user_names_log (user_id, action, changed_column, old_value, action_timestamp)
                VALUES (OLD.user_id, 'DELETE', 'all_columns', json_object('first_name', OLD.first_name, 'last_name', OLD.last_name), CURRENT_TIMESTAMP);
            END;
        """))

async def setup_user_avatars_triggers(engine):
    async with engine.begin() as conn:
        await conn.execute(text("""
            DROP TRIGGER IF EXISTS log_user_avatars_insert;
        """))
        await conn.execute(text("""
            DROP TRIGGER IF EXISTS log_user_avatars_update;
        """))
        await conn.execute(text("""
            DROP TRIGGER IF EXISTS log_user_avatars_delete;
        """))
        await conn.execute(text("""
            CREATE TRIGGER log_user_avatars_insert
            AFTER INSERT ON user_avatars
            BEGIN
                INSERT INTO user_avatars_log (user_id, action, changed_column, new_value, action_timestamp)
                VALUES (NEW.user_id, 'INSERT', 'avatar_way', NEW.avatar_way, CURRENT_TIMESTAMP);
            END;
        """))
        await conn.execute(text("""
            CREATE TRIGGER log_user_avatars_update
            AFTER UPDATE ON user_avatars
            FOR EACH ROW
            BEGIN
                INSERT INTO user_avatars_log (user_id, action, changed_column, old_value, new_value, action_timestamp)
                VALUES (OLD.user_id, 'UPDATE', 'avatar_way', OLD.avatar_way, NEW.avatar_way, CURRENT_TIMESTAMP);
            END;
        """))
        await conn.execute(text("""
            CREATE TRIGGER log_user_avatars_delete
            AFTER DELETE ON user_avatars
            BEGIN
                INSERT INTO user_avatars_log (user_id, action, changed_column, old_value, action_timestamp)
                VALUES (OLD.user_id, 'DELETE', 'avatar_way', OLD.avatar_way, CURRENT_TIMESTAMP);
            END;
        """))
