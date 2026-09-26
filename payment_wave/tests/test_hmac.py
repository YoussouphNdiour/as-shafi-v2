import hashlib
import hmac as hmac_lib

from odoo.tests import tagged, TransactionCase


def _make_signature(secret, reference):
    """Standalone HMAC-SHA256 helper mirroring the controller logic."""
    return hmac_lib.new(
        secret.encode(), reference.encode(), hashlib.sha256,
    ).hexdigest()


@tagged('post_install', '-at_install')
class TestWaveHMAC(TransactionCase):

    _SECRET = 'test-secret-wave-2026'
    _REF = 'WAVE-INV-2026-0001'

    def test_hmac_is_deterministic(self):
        """Same inputs produce identical signatures."""
        sig1 = _make_signature(self._SECRET, self._REF)
        sig2 = _make_signature(self._SECRET, self._REF)
        self.assertEqual(sig1, sig2, "HMAC must be deterministic")

    def test_hmac_varies_with_reference(self):
        """Different references produce different signatures."""
        sig1 = _make_signature(self._SECRET, self._REF)
        sig2 = _make_signature(self._SECRET, 'WAVE-INV-2026-0002')
        self.assertNotEqual(sig1, sig2, "Different refs must yield different sigs")

    def test_verify_valid_signature(self):
        """compare_digest accepts a correctly-generated signature."""
        sig = _make_signature(self._SECRET, self._REF)
        expected = _make_signature(self._SECRET, self._REF)
        self.assertTrue(
            hmac_lib.compare_digest(expected, sig),
            "Valid signature must pass verification",
        )

    def test_reject_tampered_signature(self):
        """compare_digest rejects a tampered/wrong signature."""
        sig = _make_signature(self._SECRET, self._REF)
        tampered = sig[:-4] + 'XXXX'
        expected = _make_signature(self._SECRET, self._REF)
        self.assertFalse(
            hmac_lib.compare_digest(expected, tampered),
            "Tampered signature must fail verification",
        )
