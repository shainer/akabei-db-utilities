#!/usr/bin/python3

import gnupg
import os
import sqlite3
import sys
import tarfile
import urllib.request

def GetArchiveFile(repo):
	return '%s.db.tar.xz' % repo

def GetDatabaseFile(repo):
	return '%s.db' % repo

def DownloadDatabase(repo):
	dbUrl = (
		'http://rsync.chakraos.org/packages/%s/x86_64/%s.db.tar.xz'
		% (repo, repo))
	archiveFile = GetArchiveFile(repo)

	urllib.request.urlretrieve(dbUrl, archiveFile)
	return archiveFile

def FixDatabaseGroups(dbFile):
	c = sqlite3.connect(dbFile)
	cursor = c.cursor()

	dupGroups = cursor.execute(
		'SELECT count(name) FROM groups GROUP BY name HAVING count(name) > 1').fetchall()

	if len(dupGroups) == 0:
		print ('[**] No duplicate group, just exit.')
		exit(0)

	cursor.execute(
		'DELETE FROM groups WHERE id not IN (SELECT min(id) FROM groups GROUP BY name);')

	belongsGroup = cursor.execute(
		'SELECT groupname FROM belongsgroup;').fetchall()
	c.commit()

	numErrors = 0
	for bg in belongsGroup:
		print ('Checking group %s' % bg[0])
		query = 'SELECT * FROM groups WHERE name=\'%s\'' % bg[0]
		group = cursor.execute(query).fetchall()

		if len(group) == 0:
			print ('!! Error! We removed the group %s entirely!' % bg[0])
			numErrors += 1
		elif len(group) > 1:
			print ('!! Error! The group %s still has duplicates' % bg[0])
			numErrors += 1

	c.close()
	return (numErrors == 0)

def CompressDatabase(dbFile, archiveFileName):
    tf = tarfile.open(name=archiveFileName, mode='w:xz')
    tf.add(dbFile)
    tf.close()
    return True

def SignArchive(archiveFileName):
	gpg = gnupg.GPG()
	sigName = '%s.sig' % archiveFileName	

	archiveFile = open(archiveFileName, 'rb')
	gpg.sign_file(archiveFile, output=sigName)

if __name__ == '__main__':
	if len(sys.argv) == 1:
		print('Usage: %s repo-name ' % sys.argv[0])
		exit(-1)

	repo = sys.argv[1]

	archiveFile = DownloadDatabase(repo)

	with tarfile.open(archiveFile) as f:
		f.extractall('.')
	print('[**] Decompressed database')

	dbFile = GetDatabaseFile(repo)
	success = FixDatabaseGroups(dbFile)
	if success:
		print ('[**] Packages groups fixed successfully in the database.')
	else:
		print ('[!!] Errors occurred. Exiting...')
		exit(-1)

	if not CompressDatabase(dbFile, archiveFile):
		print ("[!!] Error compressing database file.")

	print ('[**] Compressed database.')
	SignArchive(archiveFile)
