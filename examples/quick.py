from BioMetaDB import get_table
sess, Table = get_table("EcoMicroProject/config/Planctomycetes.ini", "Genomic")
print(sess.query(Table).first())

