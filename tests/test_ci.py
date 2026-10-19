"""CI acceptance contracts: target matrix, gates, and release hygiene."""
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parent.parent


def workflow(name):
    return yaml.load((ROOT/'.github/workflows'/name).read_text(), Loader=yaml.BaseLoader)


class WorkflowTests(unittest.TestCase):
    def test_all_architectures_are_explicit(self):
        jobs=workflow('pipeline.yml')['jobs']
        target=jobs['desktop']['strategy']['matrix']['include']
        self.assertTrue({('mac','arm64'),('mac','x64'),('win','arm64'),('win','x64'),
                         ('linux','arm64'),('linux','x64')}.issubset(
                         {(i['platform'],i['arch']) for i in target}))
        self.assertEqual({i['arch'] for i in jobs['ios']['strategy']['matrix']['include']},
                         {'arm64','x86_64'})
        self.assertIn('ubuntu-24.04-arm',jobs['unit']['strategy']['matrix']['os'])

    def test_deployment_and_tag_release_depend_on_tested_bundles(self):
        jobs=workflow('pipeline.yml')['jobs']
        self.assertIn('web',jobs['deploy-pages']['needs'])
        self.assertEqual(set(jobs['github-release']['needs']),{'web','android','ios','desktop'})
        self.assertIn('unit',jobs['web']['needs'])
        self.assertIn('unit',jobs['android']['needs'])

    def test_artifacts_and_signing_are_not_claimed_as_same(self):
        ci=(ROOT/'.github/workflows/pipeline.yml').read_text()
        self.assertIn('assembleDebug bundleRelease',ci)
        self.assertIn('CODE_SIGNING_ALLOWED=NO',ci)
        signed=(ROOT/'.github/workflows/android-signed.yml').read_text()
        for secret in ['ANDROID_KEYSTORE_BASE64','ANDROID_KEYSTORE_PASSWORD',
                       'ANDROID_KEY_ALIAS','ANDROID_KEY_PASSWORD']:
            self.assertIn(secret,signed)

    def test_ios_store_signing_is_explicit_opt_in(self):
        signed=workflow('ios-signed.yml')
        self.assertIn('workflow_dispatch',signed['on'])
        self.assertIn('IOS_DISTRIBUTION_CERTIFICATE_P12_BASE64',
                      (ROOT/'.github/workflows/ios-signed.yml').read_text())

if __name__=='__main__':unittest.main()
