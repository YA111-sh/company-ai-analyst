USE master;
GO
CREATE LOGIN ai_readonly
WITH PASSWORD = 'Sweetlife',
     CHECK_POLICY = OFF;


USE [WalttiPro_2.0.0];
GO
CREATE USER ai_readonly FOR LOGIN ai_readonly;



GRANT SELECT ON dbo.Company TO ai_readonly;


EXECUTE AS USER = 'ai_readonly';
SELECT TOP 5 * FROM dbo.Company;   -- should work
DELETE FROM dbo.Company;           -- should fail: permission denied
REVERT;