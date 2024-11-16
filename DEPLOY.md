# About this document

I just removed Travis integration from this project because I don't understand the errors and don't have time to fix all them so better keep this information here to run the process manually when creating a new release

    language: python
    install: echo "Nothing to install, $TRAVIS_TAG"
    script: echo "Nothing to test" && true
    before_deploy:
      - cd custom_components/diematic_3_c230_eco
      - zip -r de_dietrich_c230_ha .
    deploy:
      provider: releases
      token: $GITHUB_OAUTH_TOKEN
      tag_name: $TRAVIS_TAG
      name: $TRAVIS_TAG
      file: de_dietrich_c230_ha.zip
      cleanup: false
      draft: true
      prerelease: true
      edge: true
      on:
        tags: true
