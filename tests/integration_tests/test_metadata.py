from unittest import TestCase
from unittest import skip

from pytezos import pytezos


class TestMetadata(TestCase):
    def test_usds_all_tokens_view(self):
        usds = pytezos.using('mainnet').contract('KT1REEb5VxWRjcHm5GzDMwErMmNFftsE5Gpf')
        res = usds.metadata.allTokens().storage_view()
        self.assertEqual([0], res)

    def test_domains(self):
        td = pytezos.using('mainnet').contract('KT1GBZmSxmnKJXGMdMLbugPfLyUPmuLSMwKS')
        res = td.metadata.resolveAddress('tz1PN9FWDGoASBTvgppaQbbPdGhkrnTNmcVz').storage_view()
        self.assertEqual('tz1PN9FWDGoASBTvgppaQbbPdGhkrnTNmcVz', res['address'])
