def sort(population):
    n=len(population)
    for k in range(int(n/2),0,-1):
        downheap(population,k,n)
    while n>1:
        t=population[0]
        population[0]=population[n-1]
        population[n-1]=t
        n=n-1
        downheap(population,1,n)


def downheap(population,k,n):
    t=population[k-1]
    while k<=int(n/2):
        j=k+k
        if (j<n) and (population[j-1].get_fitness()>population[j].get_fitness()):
            j=j+1
        if t.get_fitness()<=population[j-1].get_fitness():
            break
        else:
            population[k-1]=population[j-1]
            k=j
    population[k-1]=t



