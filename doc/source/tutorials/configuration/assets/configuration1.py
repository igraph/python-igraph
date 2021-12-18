import igraph as ig

# Set configuration variables
ig.config["plotting.backend"] = "matplotlib"
ig.config["plotting.layout"] = "fruchterman_reingold"
ig.config["plotting.palette"] = "rainbow"

# Save configuration to ~/.igraphrc
ig.config.save()


