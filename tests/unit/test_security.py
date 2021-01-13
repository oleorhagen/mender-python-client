# Copyright 2021 Northern.tech AS
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import pytest

import mender.security.key as key
import mender.security.rsa as rsa


class TestSecurity:

    def test_generate_key(self):
        assert key.generate_key()

    def test_public_key(self):
        k = key.generate_key()
        assert k
        pk = key.public_key(k)
        assert len(pk) > 0

    def test_store_and_load_key(self, tmpdir):
        d = tmpdir.mkdir("store-key")
        f = d.join("script")
        k = key.generate_key()
        assert k
        key.store_key(k, f)
        with open(f):
            pass
        kn = key.load_key(f)
        assert kn

    def test_sign(self):
        k = key.load_key("tests/unit/data/keys/id_rsa")
        assert k
        sig = key.sign(k, "foobarbaz")
        assert sig
        assert sig == "T9PoH8owesBFSaFxunhm7JOmrlTwKunjtL6ct8DvLptv/SHsJyS9bF8npLhWiCtX4PqjcfcP+v9U+yG2g7IC7/mB1hRZVsWqg2D4gA0Jxuq3oRvNyB5undL+c56C4OSd4aUU/Fq86hS4L9L9Fk7B0eIwZc7WEryDJyYNuDNMJ9CJS6ul1upw8d5rF3GNjveH24TnGrpvYf5RFcHujBP0MMWayM+2iCtkHr1JEy8BDTHukH1Wh/0VRtbJ4bx55H9YYFXaH7sDhs6vPejFVMtf95LfgxI+F55p3Iu90+Hb4uSC2fPUiJ90Rs5GHiu+RzhYQEy6/z4y5pQiQ/pJqyAjdNDU/9CGWzflZdNjk3GKnY6Uic7XNphTACAxDTFWrdYrRTMOY8ovFd+/LFkU2D8Kynx9h7LwRbsD90hR98Mk97prTZCXsRQOAy5/uzMxNGlNe9zwLWDo6pn8oxFHbcV3h0Za9Q0lFep7kUF47pnXEiBg8x6sfLsMtgMSgo5ypRAn"


class TestRSA:
    def test_generate_key(self):
        pass

    def test_public_key(self):
        pass

    def test_store_key(self):
        pass

    def test_load_key(self):
        pass

    def test_sign(self):
        pass
