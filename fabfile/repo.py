from bitbucket.bitbucket import Bitbucket


def create_new_repo(username, password, name):

	bb = Bitbucket(username, password, repo_name_or_slug=name)
	success, result = bb.repository.create(name)
	
	return "git@bitbucket.org:" + username + "/" + name