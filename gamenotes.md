Rules to live by:
- The player is _always_ in control of something in some way
	- No waiting, ever, at any point. Even loading screens must be interactive
	- No popups, no stops no gaps
	- This guarantees constant action
- None or minimal sprite-work
	- everything should be drawn with shapes & pixels
- Show don't tell
	- Minimal hints, if control hints are needed then they should be small and overlaid
- The player should feel like the god of their own little world.
	- Movement should be fluid and natural
- As much as possible within the game should be intractable
- Never mention the words: 'die', 'kill', 'win', 'lose', 'game', 'lives'
- Only make games you've never played before


# growth game
- particles stick to you
- when they stick to you they move with you as part of you
- if any part of you touches the edge, you lose
- particles spawn on the edge of the screen at a random position, and move in a random direction
- particles despawn when they reach the other edge of the screen
- score based on number of particles stuck to you
	- (or maybe n of particles spawned or n or particles despawned)


### TODO:
- colours:
	- <s>particles come in different colours</s>
	- <s>particles are created with a colour and that colour increases by 1 across the rainbow</s>
	- <s>Colours should modulo within a range (eg each (r, g, b) for 50 <= r, g, b < 170)</s>
	- particles should start changing colour after a certain score
- possible sound design styles:
	- classic bleep bloop
	- something muted
- simple, minimalist menu:
	- colours get muted when you lose
	- <s>black and white, bold text, in a pixelated / classic 'code' style</s>
- Let particles collide and bounce off each other
- More little secrets in the saturation screen (random effects? different fonts? capitalised/lowercase?)
- <s>particle effects on collision</s>
- some kind of animation when you loose
- some way to avoid you being able to just sit still and let it run? bits fall off if you stop moving?
- able to change screen size in-game by just dragging window?
- particles get faster/more spawned per second as the game goes on?
- MENU with settings you can change
- Onscreen timer


### maybe?:
- adjust acceleration
- different types of particles that have different movement patterns/ cause different effects?
	- different particles appear when you are different sizes
	- different shape: (careful to not be too tetris-like)
	- different sizes: (different sizes worth different amount of points?)
	- different patterns would be different colours/have different coloured outlines
	- possible types:
		- slow/fast
		- wobbly
		- chance to bounce off you
		- chance to join together and join to you together
		- curved (angle of curvature constant per colour?
		- make you move faster/slower
		- delete particles off you??? (difficult as would have to deal with bits falling off you - intensive)
- sounds change as game goes on
	- each particle makes a small quiet noise at a particular pitch - as you grow, more and more sounds (very loud when near max)