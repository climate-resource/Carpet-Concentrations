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

#### PyPI

This step can be skipped if you give the CI a global token for PyPI. However,
we don't recommend doing this. Assuming you want to generate a PyPI token just
for this project, the first thing you have to do is push your project to PyPI.
Once setup, this will happen automatically, but the first one has to be done
locally.

To do this, firstly tag the project locally with "v0.1.0". It doesn't really
matter which commit you do this on.

Then, build the project locally with

```bash
poetry build
```

Assuming this runs without error, setup poetry so it can push to PyPI (or skip
this step and just pass your username and password in the next step). You can
either do this with a token or your username and password (also see
[the box here](https://python-poetry.org/docs/repositories/#configuring-credentials)).

```bash
# token based (this token will need global scope for the first push)
poetry config pypi-token.pypi <my-token>
# password based
poetry config http-basic.pypi <username> <password>
```

Then, publish the package to PyPI.

```bash
poetry publish
# Alternately pass username and password with
poetry publish --username=USERNAM --password=PASSWORD
```

Assuming this runs smoothly, your package is now on PyPI. You can generate a
token just for your package that can be used by GitLab in the CI by going to
PyPI -> Account settings (in drop down under your name) -> API tokens -> Add
API token -> create a token just for this package.

#### GitHub

Create a [personal access token](https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#about-personal-access-tokens)
that can be used to write to the repository as part of GitHub actions. It is best to use the fine-grained tokens and only give the token access to this repository. The token will need "Contents" permissions, specifically read and write access for "Contents".

If you can't create a token, the organisation may need to enable personal access token access. Please ask one of the lead developers.
[TODO: write docs about getting secrets.PERSONAL_ACCESS_TOKEN setup properly]

Once you have your token, add it to a repository secret (Settings ->
Secrets and variables -> Actions -> New repository secret) called
`PERSONAL_ACCESS_TOKEN`.

Finally, add a PYPI token for the project to a repository secret (Settings ->
Secrets and variables -> Actions -> New repository secret) called `PYPI_TOKEN`.
We recommend restricting your PyPI access token so it only has the scope of
this project.

### Standard process

Releasing is semi-automated. The steps required are the following:

1. Bump the version: manually trigger the "bump" workflow from the main branch
   (see here:
   https://github.com/climate-resource/Carpet-Concentrations/actions/workflows/bump.yaml).
   [TODO careful propagating this]
   This will then trigger a draft release.

1. Edit the draft release which has been created
   (see here:
   https://github.com/climate-resource/Carpet-Concentrations/releases).
   [TODO careful propagating this]
   Once you are happy with the release (removed placeholders, added key
   announcements etc.) then hit 'Publish release'. This triggers a release to
   PyPI (which you can then add to the release if you want).

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
