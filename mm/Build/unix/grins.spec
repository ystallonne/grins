product grins
    id "GRiNS Player 0.5"
    cutpoint usr/grins
    image sw
        id "GRiNS Player 0.5 Software"
        version 2
        order 9999
        subsys player default
            id "GRiNS Player 0.5 Base Software"
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
            exp grins.sw.player
        endsubsys
    endimage
    image help
        id "GRiNS Player 0.5 Help Files"
        version 2
        order 9999
        subsys examples default
            id "GRiNS Player 0.5 SMIL Examples"
            replaces self
            prereq (
                grins.sw.player 2 2
            )
            exp grins.help.examples
        endsubsys
        subsys documentation default
            id "GRiNS Player 0.5 Documentation"
            replaces self
            exp grins.help.documentation
        endsubsys
    endimage
    image relnotes
        id "GRiNS Player 0.5 Release Notes"
        version 2
        order 9999
        subsys relnotes default
            id "GRiNS Player 0.5 Release Notes"
            replaces self
            exp grins.relnotes.relnotes
        endsubsys
    endimage
endproduct
