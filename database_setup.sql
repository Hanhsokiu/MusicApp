USE master;
GO

IF DB_ID(N'MusicApp_test') IS NULL
BEGIN
    CREATE DATABASE MusicApp_test;
END
GO

USE MusicApp_test;
GO

IF OBJECT_ID(N'dbo.PlaylistSongs', N'U') IS NOT NULL
    DROP TABLE dbo.PlaylistSongs;
GO

IF OBJECT_ID(N'dbo.Playlists', N'U') IS NOT NULL
    DROP TABLE dbo.Playlists;
GO

IF OBJECT_ID(N'dbo.Favorites', N'U') IS NOT NULL
    DROP TABLE dbo.Favorites;
GO

IF OBJECT_ID(N'dbo.Recent', N'U') IS NOT NULL
    DROP TABLE dbo.Recent;
GO

IF OBJECT_ID(N'dbo.Songs', N'U') IS NOT NULL
    DROP TABLE dbo.Songs;
GO

IF OBJECT_ID(N'dbo.Users', N'U') IS NOT NULL
    DROP TABLE dbo.Users;
GO

CREATE TABLE dbo.Users
(
    id INT IDENTITY(1,1) NOT NULL,
    username NVARCHAR(50) NOT NULL,
    [password] NVARCHAR(255) NOT NULL,
    [role] NVARCHAR(20) NOT NULL
        CONSTRAINT DF_Users_Role DEFAULT N'user',

    CONSTRAINT PK_Users PRIMARY KEY (id),
    CONSTRAINT UQ_Users_Username UNIQUE (username),
    CONSTRAINT CK_Users_Role CHECK ([role] IN (N'admin', N'user'))
);
GO

CREATE TABLE dbo.Songs
(
    id INT IDENTITY(1,1) NOT NULL,
    title NVARCHAR(255) NOT NULL,
    artist NVARCHAR(255) NOT NULL,
    fileUrl NVARCHAR(500) NOT NULL,
    imageUrl NVARCHAR(500) NULL,

    CONSTRAINT PK_Songs PRIMARY KEY (id)
);
GO

CREATE TABLE dbo.Favorites
(
    userId INT NOT NULL,
    songId INT NOT NULL,

    CONSTRAINT PK_Favorites PRIMARY KEY (userId, songId),
    CONSTRAINT FK_Favorites_Users FOREIGN KEY (userId)
        REFERENCES dbo.Users(id)
        ON DELETE CASCADE,
    CONSTRAINT FK_Favorites_Songs FOREIGN KEY (songId)
        REFERENCES dbo.Songs(id)
        ON DELETE CASCADE
);
GO

CREATE TABLE dbo.Recent
(
    id INT IDENTITY(1,1) NOT NULL,
    userId INT NOT NULL,
    songId INT NOT NULL,
    playedAt DATETIME NOT NULL
        CONSTRAINT DF_Recent_PlayedAt DEFAULT GETDATE(),

    CONSTRAINT PK_Recent PRIMARY KEY (id),
    CONSTRAINT FK_Recent_Users FOREIGN KEY (userId)
        REFERENCES dbo.Users(id)
        ON DELETE CASCADE,
    CONSTRAINT FK_Recent_Songs FOREIGN KEY (songId)
        REFERENCES dbo.Songs(id)
        ON DELETE CASCADE
);
GO

CREATE TABLE dbo.Playlists
(
    id INT IDENTITY(1,1) NOT NULL,
    userId INT NOT NULL,
    name NVARCHAR(100) NOT NULL,
    createdAt DATETIME NOT NULL
        CONSTRAINT DF_Playlists_CreatedAt DEFAULT GETDATE(),

    CONSTRAINT PK_Playlists PRIMARY KEY (id),
    CONSTRAINT FK_Playlists_Users FOREIGN KEY (userId)
        REFERENCES dbo.Users(id)
        ON DELETE CASCADE
);
GO

CREATE TABLE dbo.PlaylistSongs
(
    id INT IDENTITY(1,1) NOT NULL,
    playlistId INT NOT NULL,
    songId INT NOT NULL,
    addedAt DATETIME NOT NULL
        CONSTRAINT DF_PlaylistSongs_AddedAt DEFAULT GETDATE(),

    CONSTRAINT PK_PlaylistSongs PRIMARY KEY (id),
    CONSTRAINT FK_PlaylistSongs_Playlists FOREIGN KEY (playlistId)
        REFERENCES dbo.Playlists(id)
        ON DELETE CASCADE,
    CONSTRAINT FK_PlaylistSongs_Songs FOREIGN KEY (songId)
        REFERENCES dbo.Songs(id)
        ON DELETE CASCADE,
    CONSTRAINT UQ_PlaylistSongs UNIQUE (playlistId, songId)
);
GO

CREATE INDEX IX_Favorites_SongId
ON dbo.Favorites(songId);
GO

CREATE INDEX IX_Recent_UserId_PlayedAt
ON dbo.Recent(userId, playedAt DESC);
GO

CREATE INDEX IX_Playlists_UserId
ON dbo.Playlists(userId);
GO

CREATE INDEX IX_PlaylistSongs_PlaylistId
ON dbo.PlaylistSongs(playlistId);
GO

CREATE INDEX IX_PlaylistSongs_SongId
ON dbo.PlaylistSongs(songId);
GO

INSERT INTO dbo.Songs (title, artist, fileUrl, imageUrl)
VALUES
(N'TRÌNH', N'Đen', N'/uploads/1774359796_TRÌNH.mp3', NULL),
(N'TRÌNH Ver 2', N'Đen', N'/uploads/1774360025_TRÌNH.mp3', NULL),
(N'Hôn Lễ Của Em', N'Quang Hùng MasterD', N'/uploads/1774360083_Hôn Lễ Của Em.mp3', NULL),
(N'Anh Tên Là', N'Orange', N'/uploads/1774360157_Anh Tên Là.mp3', NULL),
(N'Người Im Lặng Gặp Người Hay Nói', N'Unknown Artist', N'/uploads/1774360216_Người Im Lặng Gặp Người Hay Nói.mp3', NULL),
(N'Tấm Lòng Cửu Long', N'Unknown Artist', N'/uploads/1774360266_Tấm Lòng Cửu Long.mp3', NULL),
(N'50 Năm Về Sau', N'Unknown Artist', N'/uploads/1774360336_50 Năm Về Sau.mp3', NULL),
(N'Cỏ Dại Và Hoa Dành Dành', N'Unknown Artist', N'/uploads/1774361480_Cỏ Dại Và Hoa Dành Dành.mp3', NULL),
(N'Tấm Lòng Cửu Long Ver 2', N'Unknown Artist', N'/uploads/1774365647_Tấm Lòng Cửu Long.mp3', NULL),
(N'50 Năm Về Sau Ver 2', N'Unknown Artist', N'/uploads/1774365774_50 Năm Về Sau.mp3', N'/uploads/img_1774365774_50namvesau.jpg'),
(N'Không Buông', N'Unknown Artist', N'/uploads/1774368857_Không Buông.mp3', N'/uploads/img_1774368857_khongbuong.jpg'),
(N'Người Đầu Tiên', N'Đức Phúc', N'/uploads/1774421558_Người Đầu Tiên.mp3', N'/uploads/img_1774421558_ndt.webp');
GO

SELECT * FROM dbo.Users;
SELECT * FROM dbo.Songs;
SELECT * FROM dbo.Favorites;
SELECT * FROM dbo.Recent;
SELECT * FROM dbo.Playlists;
SELECT * FROM dbo.PlaylistSongs;
GO
