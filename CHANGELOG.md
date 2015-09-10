# v0.1.0 (xxxx-xx-xx)

## Summary

* Rename *LCONF* to **PyLCONF**.
* Implementation of the new *LCONF-Data-Serialization-Format-Standard* **v0.1.0**.
* Adds suport for working with the new LCONF-Schema.
* Change to P-Versioning Based On [Semantic Versioning](http://semver.org/). Restart with version `0.1.0`.

# History

* In early 2014 **peter1000** <https://github.com/peter1000/> released a first *LCONF* specification and an
    implementation as Julia library.

* 2014-10-08 the last *LCONF* Version 7.0.0  was released.

-----------------------------------------------------------------------------------------------------------------------

# P-Versioning Based On [Semantic Versioning](http://semver.org/)

**IMPORTANT DIFFERENCE** to the *Semantic Versioning 2.0.0* <br />

* A pre-release version MUST NOT be added.

* Build metadata MUST comprise only ASCII alphanumerics [0-9A-Za-z] and MUST NOT contain any hyphen.

## Package Versioning

1. **Software and related packages using this modified Semantic Versioning MUST declare a public API.** This API could
    be declared in the code itself or exist strictly in documentation. However it is done, it should be precise and
    comprehensive.

2. A normal version number MUST take the form X.Y.Z where X, Y, and Z are non-negative integers, and MUST NOT contain
    leading zeroes. X is the major version, Y is the minor version, and Z is the patch version.
    Each element MUST increase numerically. For instance: 1.9.0 -> 1.10.0 -> 1.11.0.

3. Once a versioned package has been released, the contents of that version MUST NOT be modified. Any modifications
    MUST be released as a new version.

4. Major version zero (0.y.z) is for initial development. Anything may change at any time. The public API should not be
    considered stable.

5. **Version 1.0.0 defines the public API. The way in which the version number is incremented after this release is
    dependent on this public API and how it changes.**

6. Patch version Z (x.y.Z | x > 0) MUST be incremented if only backwards compatible bug fixes are introduced. A bug fix
    is defined as an internal change that fixes incorrect behavior.

7. Minor version Y (x.Y.z | x > 0) MUST be incremented if new, backwards compatible functionality is introduced to the
    public API. It MUST be incremented if any public API functionality is marked as deprecated. It MAY be incremented
    if substantial new functionality or improvements are introduced within the private code. It MAY include patch level
    changes. Patch version MUST be reset to 0 when minor version is incremented.

8. Major version X (X.y.z | X > 0) MUST be incremented if any backwards incompatible changes are introduced to the
    public API. It MAY include minor and patch level changes. Patch and minor version MUST be reset to 0 when major
    version is incremented.

9. Build metadata MAY be denoted by appending a plus sign and a series of dot separated identifiers immediately
    following the patch version. Identifiers MUST comprise only ASCII alphanumerics [0-9A-Za-z] and MUST NOT contain
    hyphen. Identifiers MUST NOT be empty. Build metadata SHOULD be ignored when determining version precedence. Thus
    two versions that differ only in the build metadata, have the same precedence. <br />
    Examples: 1.0.0+001, 1.0.0+20130313144700, 1.0.0+exp.sha.5114f85, 1.0.7+r128.g4560914.

* What do I do if I accidentally release a backwards incompatible change as a minor version?

    As soon as you realize that you've broken the Semantic Versioning spec, fix the problem and release a new minor
    version that corrects the problem and restores backwards compatibility. Even under this circumstance, it is
    unacceptable to modify versioned releases. If it's appropriate, document the offending version and inform your
    users of the problem so that they are aware of the offending version.

* How should I handle deprecating functionality?

    Deprecating existing functionality is a normal part of software development and is often required to make forward
    progress. When you deprecate part of your public API, you should do two things:

    1. update your documentation to let users know about the change,
    2. issue a new minor release with the deprecation in place. Before you completely remove the functionality in a new
        major release there should be at least one minor release that contains the deprecation so that users can
        smoothly transition to the new API.
