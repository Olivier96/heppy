from numpy import linalg, array, zeros


def eventShape(particles):
    tensor = zeros((3,3))
    denom = 0.
    for particle in particles:
        denom += particle.P()*particle.P()
        for i in range(3):
            for j in range(3):
                tensor[i,j] += particle[i]*particle[j]

    tensor *= 1./denom

    values, vectors = linalg.eig(tensor)

    def getKey(item):
        return item[0]

    keyVectors = []
    eigValues = []
    eigVectors = []
    for i,v in enumerate(vectors):
        keyVectors.append([values[i],v])
    keyVectors.sort(key=getKey, reverse=True)
    for i,v in enumerate(keyVectors):
        eigVectors.append(v[1])
        eigValues.append(v[0])

    sphericity = 1.5*(eigValues[1]+eigValues[2])
    aplanarity = 1.5*eigValues[2]
    planarity = 2./3.*(sphericity - 2.*aplanarity)

    return sphericity, aplanarity, planarity, eigVectors[0]
