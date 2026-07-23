FROM odoo:17

USER root

# Install additional dependencies for custom modules
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Create addons directory
RUN mkdir -p /mnt/extra-addons && chown -R odoo:odoo /mnt/extra-addons

USER odoo

EXPOSE 8069
