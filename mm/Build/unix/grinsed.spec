product grinsed
    id "GRiNS for SMIL 1.0"
    cutpoint usr/local/grins
    image sw
        id "GRiNS 1.0 Software"
        version 10000
        order 9999
        subsys editor default
            id "GRiNS Editor for SMIL 1.0 Base Software"
            replaces self
            prereq (
                compiler_eoe.sw.lib 1275056010 maxint
                dmedia_eoe.sw.audio 1275093220 maxint
                dmedia_eoe.sw.lib 1275093220 maxint
                eoe.sw.base 1275093236 maxint
                eoe.sw.gfx 1275093236 maxint
                motif_eoe.sw.eoe 1275093220 maxint
                x_eoe.sw.eoe 1275093220 maxint
            )
            exp grinsed.sw.editor
        endsubsys
        subsys player default
            id "GRiNS Player for SMIL 1.0 Base Software"
            replaces self
            replaces grins.sw.player 10000 10000
            prereq (
                compiler_eoe.sw.lib 1275056010 maxint
                dmedia_eoe.sw.audio 1275093220 maxint
                dmedia_eoe.sw.lib 1275093220 maxint
                eoe.sw.base 1275093236 maxint
                eoe.sw.gfx 1275093236 maxint
                motif_eoe.sw.eoe 1275093220 maxint
                x_eoe.sw.eoe 1275093220 maxint
            )
            exp grinsed.sw.player
        endsubsys
        subsys templates default
            id "GRiNS Editor for SMIL 1.0 Templates"
            replaces self
            prereq (
                grinsed.sw.editor 10000 10000
            )
            exp grinsed.sw.templates
        endsubsys
    endimage
    image help
        id "GRiNS for SMIL 1.0 Help Files"
        version 10000
        order 9999
        subsys examples default
            id "GRiNS for SMIL 1.0 SMIL Examples"
            replaces self
	    replaces grins.help.examples 10000 10000
            prereq (
                grinsed.sw.editor 10000 10000
            )
            prereq (
                grinsed.sw.player 10000 10000
            )
            exp grinsed.help.examples
        endsubsys
        subsys documentation default
            id "GRiNS Editor for SMIL 1.0 Documentation"
            replaces self
	    replaces grins.help.documentation 10000 10000
            exp grinsed.help.documentation
        endsubsys
    endimage
    image relnotes
        id "GRiNS for SMIL 1.0 Release Notes"
        version 10000
        order 9999
        subsys relnotes default
            id "GRiNS for SMIL 1.0 Release Notes"
            replaces self
            replaces grins.relnotes.relnotes 10000 10000
            exp grinsed.relnotes.relnotes
        endsubsys
    endimage
endproduct
