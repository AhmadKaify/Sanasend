-- SQL to rename tables from whatsapp_* to sessions/messages prefixes
-- Run this if you have existing data in the database

-- Rename sessions tables
ALTER TABLE whatsapp_sessions_whatsappsession RENAME TO sessions_whatsappsession;

-- Rename messages tables  
ALTER TABLE whatsapp_messages_message RENAME TO messages_message;

