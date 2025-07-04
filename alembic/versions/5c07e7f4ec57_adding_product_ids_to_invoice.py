"""adding product_ids to invoice

Revision ID: 5c07e7f4ec57
Revises: 4bd28552afb2
Create Date: 2025-07-03 16:50:55.474463

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5c07e7f4ec57'
down_revision: Union[str, Sequence[str], None] = '4bd28552afb2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_admin_admin_id'), table_name='admin')
    op.drop_index(op.f('ix_customers_customer_id'), table_name='customers')
    op.add_column('invoices', sa.Column('product_ids', sa.JSON(), nullable=True))
    op.drop_index(op.f('ix_invoices_invoice_id'), table_name='invoices')
    op.drop_index(op.f('ix_orders_order_id'), table_name='orders')
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)
    op.create_index(op.f('ix_orders_order_id'), 'orders', ['order_id'], unique=False)
    op.create_index(op.f('ix_invoices_invoice_id'), 'invoices', ['invoice_id'], unique=False)
    op.drop_column('invoices', 'product_ids')
    op.create_index(op.f('ix_customers_customer_id'), 'customers', ['customer_id'], unique=False)
    op.create_index(op.f('ix_admin_admin_id'), 'admin', ['admin_id'], unique=False)
    # ### end Alembic commands ###
