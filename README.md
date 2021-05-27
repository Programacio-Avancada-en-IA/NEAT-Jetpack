# NEAT-Jetpack

### Ús de visualize.py
Cada vegada que s'acaba una generació es fa una grafica amb les neurones i connexions actuals del genoma que ha durat més,
on:  
Línia sòlida vol dir Connexió activada i amb punts vol dir desactivada  
Verd vol dir pes > 0 i roig pes < 0

## Performance analysis
#### 5 inputs, pop 20
Due to the small population size, improval is very rare. It has taken more than 20 generations to start getting past more than 150 
fitness, which has been done purely out of luck. Still by generation 30 almost no visible improval is seen. By generation 36, 
the total record is 172 fitness.

#### 5 inputs, pop 100
A vast improvement is seen just by increasing the population size to 100, which reaches 600 fitness in just gen 2. This happens
because the amount of population generates a lot more random possibilities, and thus getting us closer to a good AI in less time.
On generation 12, the players have realized how to avoid obstacles and that they get bonus fitness for staying off the ground and
away from the ceiling, reaching 1200 fitness.

#### 5 inputs, pop 200
By doubling the population, as expected, we get the same results in half the time. 

#### 9 inputs, pop 20
If we use 9 inputs, we can also give to the player information about the next 2 lasers in order to have more anticipation. 
However, with just 20 members, we face the same problems as before, evolution is slow and high scores are purely based on luck.
The most notable example is when a species gets a really high score by staying on the ceiling, and then when a laser appears on
the ceiling nothing is done to dodge it. No real improvement except staying on the ceiling has been made by gen 24. (OVERFITTING)

#### 9 inputs, pop 100
With 9 inputs and a population of 100, it takes approximately 15 generations to realize the importance of not staying always 
in the ceiling, finally obtaining players actively dodging obstacles. However, it also takes some luck to get past 1000 by gen 10,
because of the possible overfitting caused by obstacles not appearing on the ceiling or ground.

#### 9 inputs, pop 200
With 200 players per gen, we can see a player reach a fitness of 900 by gen 9. The large amount of players makes learning faster 
and more resistant to overfitting. A few generations later, at gen 21, it has reached 100000.
