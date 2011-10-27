Development of :mod:`AstroObject`
=================================

I'm developing this module to support my own Astronomical Data reduction. As this is an early release (|release|), it lacks many features. My general development philosophy is as follows:

Build features that I need, when I need them. Discover bugs as I go along, and squash those bugs when I can. Maintain relatively stable APIs which are gracefully depreciated over multiple minor versions at minimum, but make no guarantee that the APIs will stay this way. Leave features partially implemented when I don't need much of their functionality.

In many ways, this constitutes "agile" development. That means that I can't/won't guarantee what works and doesn't in this library now, or later, until I decide to release a version 1.0

That being said, I'd love help. If you have development ideas or principles that I should include, or if you think that this project would be well suited in some other environment, please let me know. If you have patches and development assistance, let me know about that as well.

At this time, I'm not posting the development branch to Github. If you want to help develop, let me know, and I will start posting the development branch.

Methods of Development
----------------------

Very briefly, this project is using Github for source control, and using git flow for feature and release management. As of |release|, I'm developing nosetests for the system and API, as well as this documentation.