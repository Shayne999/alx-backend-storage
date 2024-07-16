#!/usr/bin/env python3
"""Inserts a document in a collection based on kwargs"""
import pymongo


def insert_school(mongo_collection, **kwargs):
    """Inserts a document in a collection"""
    return mongo_collection.insert_one(kwargs).inserted_id
