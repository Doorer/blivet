#!/usr/bin/python
import baseclass
import os
import unittest
import time

import blivet.devicelibs.mdraid as mdraid
import blivet.errors as errors

class MDRaidTestCase(unittest.TestCase):

    def testMDRaid(self):

        ##
        ## getRaidLevel
        ##
        self.assertEqual(mdraid.getRaidLevel("container").name, "container")
        self.assertEqual(mdraid.getRaidLevel("stripe").name, "raid0")
        self.assertEqual(mdraid.getRaidLevel("mirror").name, "raid1")
        self.assertEqual(mdraid.getRaidLevel("4").name, "raid4")
        self.assertEqual(mdraid.getRaidLevel(5).name, "raid5")
        self.assertEqual(mdraid.getRaidLevel("RAID6").name, "raid6")
        self.assertEqual(mdraid.getRaidLevel("raid10").name, "raid10")

        ##
        ## get_raid_superblock_size
        ##
        self.assertEqual(mdraid.get_raid_superblock_size(256 * 1024), 128)
        self.assertEqual(mdraid.get_raid_superblock_size(128 * 1024), 128)
        self.assertEqual(mdraid.get_raid_superblock_size(64 * 1024), 64)
        self.assertEqual(mdraid.get_raid_superblock_size(63 * 1024), 32)
        self.assertEqual(mdraid.get_raid_superblock_size(10 * 1024), 8)
        self.assertEqual(mdraid.get_raid_superblock_size(1024), 1)
        self.assertEqual(mdraid.get_raid_superblock_size(1023), 0)
        self.assertEqual(mdraid.get_raid_superblock_size(512), 0)

        self.assertEqual(mdraid.get_raid_superblock_size(257, "version"),
           mdraid.MD_SUPERBLOCK_SIZE)


class MDRaidAsRootTestCase(baseclass.DevicelibsTestCase):

    @unittest.skipUnless(os.geteuid() == 0, "requires root privileges")
    def testMDRaidAsRoot(self):
        _LOOP_DEV0 = self._loopMap[self._LOOP_DEVICES[0]]
        _LOOP_DEV1 = self._loopMap[self._LOOP_DEVICES[1]]

        ##
        ## mdcreate
        ##
        # pass
        self.assertEqual(mdraid.mdcreate("/dev/md0", 1, [_LOOP_DEV0, _LOOP_DEV1]), None)
        # wait for raid to settle
        time.sleep(2)

        # fail
        self.assertRaises(mdraid.MDRaidError, mdraid.mdcreate, "/dev/md1", 1, ["/not/existing/dev0", "/not/existing/dev1"])

        ##
        ## mddeactivate
        ##
        # pass
        self.assertEqual(mdraid.mddeactivate("/dev/md0"), None)

        # fail
        self.assertRaises(mdraid.MDRaidError, mdraid.mddeactivate, "/not/existing/md")

        ##
        ## mdadd
        ##
        # pass
        # TODO

        # fail
        self.assertRaises(mdraid.MDRaidError, mdraid.mdadd, "/not/existing/device")

        ##
        ## mdactivate
        ##
        self.assertRaises(mdraid.MDRaidError, mdraid.mdactivate, "/not/existing/md", uuid=32)
        # requires uuid
        self.assertRaises(mdraid.MDRaidError, mdraid.mdactivate, "/dev/md1")

        ##
        ## mddestroy
        ##
        # pass
        self.assertEqual(mdraid.mddestroy(_LOOP_DEV0), None)
        self.assertEqual(mdraid.mddestroy(_LOOP_DEV1), None)

        # pass
        # Note that these should fail because mdadm is unable to locate the
        # device. The mdadm Kill function does return 2, but the mdadm process
        # returns 0 for both tests.
        self.assertIsNone(mdraid.mddestroy("/dev/md0"))
        self.assertIsNone(mdraid.mddestroy("/not/existing/device"))


def suite():
    suite1 = unittest.TestLoader().loadTestsFromTestCase(MDRaidTestCase)
    suite2 = unittest.TestLoader().loadTestsFromTestCase(MDRaidAsRootTestCase)
    return unittest.TestSuite([suite1, suite2])


if __name__ == "__main__":
    unittest.main()
