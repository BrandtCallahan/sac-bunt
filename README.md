# Sacrifice Bunt Simulation (sac-bunt)

Traditional baseball knowledge says that a sacrifice bunt plays a team into a higher likelihood to score than to play out the inning without a bunt (i.e. let the player swing away). I have set out to check that knowledge and set up a simulation that will have a team's lineup run through innings that include a sac bunt and innings that do not include a sac bunt. The major distinction in these innings is that with a sac bunt we will have the runner starting on either 2nd or 3rd with 1 out (via the sacrifice) to be the 'sac bunt inning' and man on 1st or 2nd with 0 outs to be the 'swing away inning.' In my simulation each inning scenario will be played out 20,000 times and a run scoring probability will be returned for both scenarios (this probability is calculated by the percentage of innings that a run was scored). 

I have chosen to use the scenario that came up in Game 2 of this year's (2025) NLDS between the Los Angeles Dodgers and Philadelphia Phillies as my default scenario in the playball_sim() function. In the 9th inning of this game the Phillies came up to bat trailing the Dodgers 4-1. Alec Bohm opened the inning singling followed by J.T. Realmuto doubling setting up Nick Castellanos for his owning double earning him 2 RBIs. At this moment the Phillies still trailed by 1 with 0 outs in the inning. A decision was to be made though as the Phillies were heading into the bottom third of their lineup needing to push Castellanos across to tie up the game and ensure (at the very least) tying up the game and sending it to extra innings. The scenarios: <br>

1. Have Bryson Stott lay down a bunt sacrificing himself while advancing Castellanos to 3rd with only 1 out. <br>
or <br>
2. Allow Bryson Stott to swing away and give your lineup 3 full chances to drive in Castellanos and possibly set up the chance for 2 runs and a victory. <br>
<br>

| Play Type | Scenario Setup | Run % | Multi Run % |
| :-------: | :------: | :-------: | :-------: |
| Swing Away     | Runner on 2nd w/ 0 Out | 31%    | 18%    |
| Sac Bunt   | Runner on 3rd w/ 1 Out   | 30%   | 12%   |

Taking these percentages into account the Phillies could ultimately choose either option if their goal was to just tie the game in the inning at hand as the scoring percentage for just a single run is ever so slightly different (from 31% to 30%). But if the Phillies were wanting to play for the win in the moment I would have their multiple run probability being higher by allowing Stott to swing away and let the inning play out without a sacrifice bunt.

As the game actually played out we saw the Phillies elect to have Stott attempt a sac bunt and that bunt consequentially played in to the Dodgers executing a perfect wheel route and getting Castellanos at 3rd. The inning would finish out with the Phillies failing to score the tying run and ultimately losing the game, leaving the viewer (and arm chair coaches everywhere wondering: What would have happened if the Phillies would have let Stott swing away?). 
