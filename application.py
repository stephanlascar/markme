# -*- coding: utf-8 -*-
import os
import markme


app = markme.create_app(os.environ['MONGOLAB_URI'])
