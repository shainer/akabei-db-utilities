#!/usr/bin/python3

import sys
import tarfile
import wget

if __name__ == '__main__':
	if len(sys.argv == 1):
		print('Usage: %s repo-name ' % sys.argv[0])
		exit(-1)

	repo = sys.argv[1]
	dbUrl = (
		'http://rsync.chakraos.org/packages/%s/x86_64/%s.db.tar.xz'
		% (repo, repo))

	archiveFile = wget.download(dbUrl)
	with tarfile.open(archiveFile) as f:
		f.extractall('.')

	print('[**] Decompressed database')