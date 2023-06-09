(development-reference)=
# Development

Notes for developers. If you want to get involved, please do!

## Versioning

This package follows the version format described in
[PEP440](https://peps.python.org/pep-0440/) and
[Semantic Versioning](https://semver.org/). Since our commit messages are
written to follow the
[conventional commits](https://www.conventionalcommits.org/en/v1.0.0/)
specification, comitizen can use the commit messages since the last release to
determine whether a major, minor or patch release is required automatically.
See the docs for the
[commitizen bump](https://commitizen-tools.github.io/commitizen/bump/)
command for additional details about the version bumping process and
[](releasing-reference) for additional details about how we do releases in
this project.

(releasing-reference)=
## Releasing

### Initial setup

If this is the first time you're setting up the repository, read this section.
If this repository is already setup, you can skip it.

[TODO: write docs about getting secrets.PERSONAL_ACCESS_TOKEN setup properly]

### Standard process

Releasing is semi-automated. The steps required are the following:

[TODO write these steps]

1. That's it, release done, make noise on social media of choice, do whatever
   else

1. Enjoy the newly available version

## Read the Docs

Our documentation is hosted by
[Read the Docs (RtD)](https://www.readthedocs.org/), a service for which we are
very grateful. The RtD configuration can be found in the `.readthedocs.yaml`
file in the root of this repository. The docs are automatically
deployed at
[carpet-concentrations.readthedocs.io](https://carpet-concentrations.readthedocs.io/en/latest/).

### Initial setup

At the moment, we only integrate with readthedocs.org hence this setup only
works for public repositories. If you want to host docs for a private
repository, you will need to get setup with
[Read the Docs for Business](https://about.readthedocs.com/about/).

If you haven't already, you will need to link your GitLab account with RtD.
This can be done by creating an account with [RtD](https://readthedocs.org/)
and then going to
[Settings -> Connected services](https://readthedocs.org/accounts/social/connections/).
From here, the connection can be trivially added by pressing
"Connect to GitHub" and following the prompts. [TODO careful when copying this to copier repo because of GitHub]

### Adding your project

Go to your [RtD dashboard](https://readthedocs.org/dashboard/) then press
"Import a Project". Pick your project from the list then simply follow the
setup instructions (you can mostly just leave the defaults as they are, the
only thing we have done in the past is adding tags).

Once your project is working with RtD, we recommend going to Admin -> Advanced
Settings and ticking the "Build pull requests for this project" box. That will
cause the docs to be built on all pull requests, which gives fast feedback
about whether a change will a) break the docs and b) cause the docs to be
updated in the expected way.

It is also worth going to Versions and making sure that the "latest" (
generally the last commit merged to main) and "stable" versions are both
active so that users can see docs for both these versions.
